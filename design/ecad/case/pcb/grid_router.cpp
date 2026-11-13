// grid_router.cpp: negotiated-congestion grid router for the case main board (PathFinder style).
// Build:  clang++ -O2 -std=c++17 -o grid_router grid_router.cpp      Run: grid_router route_in.txt route_out.txt [seconds] [seed]
// Rules it keeps (all distances are centre line distances on a 0.05 mm grid, Manhattan moves only, through vias only):
//   track to copper of another net  >= clearance + (w_a + w_b) / 2 ; via pad to copper >= clearance + via radius + w / 2 ; via to via >= clearance + 2 via radius
//   hole to hole >= hole_to_hole ; copper to board edge >= edge clearance ; nothing inside keepout rectangles.
// Own routes may overlap each other only while negotiating; the final answer has zero overlaps or the run says so.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <vector>
#include <string>
#include <queue>
#include <algorithm>
#include <chrono>
#include <map>
#include <set>
#include <cstdint>
using namespace std;

static double X0, Y0, PITCH;
static const double PADX = 0.003;   // extra gap track to pad copper: keeps the 0.05 mm solder mask opening clear of the track (mask-to-copper clearance 0.05)
static int NX, NY, NL = 4, NCL = 4, NK = 6;  // classes 0..3 tracks, 4 = via (as a copper disc), 5 spare
static double WIDTH[8];
static double CLEAR, VIAR, VIADR, HOLEHOLE, EDGE;
struct Net { int id; int cls; string name; };
static vector<Net> nets;
struct Rect { int mask; int net; double x0, y0, x1, y1; };
struct Circ { int mask; int net; double cx, cy, r; };
struct Hole { double cx, cy, rx, ry; };
struct Term { int net; int g; int mask; double x0, y0, x1, y1; };
static vector<Rect> rects; static vector<Circ> circs; static vector<Hole> holes; static vector<Hole> qholes; static vector<Rect> keeps;
static vector<pair<double,double>> poly; static vector<Term> terms;

static inline int cellIdx(int x, int y) { return y * NX + x; }
static int NC;                           // cells per layer
static vector<int16_t> fixedOwner[8];    // [class] -> [layer*NC + cell]  (-1 free, >=0 owner net, -2 blocked for all)
static vector<int16_t> occ[8];           // dynamic counts of other nets' copper, same indexing
static vector<float> hist;               // history cost per layer*NC+cell
static vector<uint8_t> noVia;            // cells where a via must not be (near any pad)
static vector<uint8_t> noViaG;           // same for ground vias: pads of the ground net itself only need a 0.02 mm gap
static vector<uint8_t> inside;           // inside the board polygon

static double cwx(int x) { return X0 + x * PITCH; }
static double cwy(int y) { return Y0 + y * PITCH; }

static double radiusFor(int cls, int other_cls) {      // centre distance needed between copper of class cls and class other_cls
    double wa = cls == 4 ? 2 * VIAR : WIDTH[cls];
    double wb = other_cls == 4 ? 2 * VIAR : WIDTH[other_cls];
    return CLEAR + (wa + wb) / 2;
}

static void markRectDisk(int k, int layer, int owner, double x0, double y0, double x1, double y1, double R) {
    int ix0 = max(0, (int)floor((x0 - R - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((x1 + R - X0) / PITCH));
    int iy0 = max(0, (int)floor((y0 - R - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((y1 + R - Y0) / PITCH));
    for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) {
        double px = cwx(x), py = cwy(y);
        double dx = max(max(x0 - px, 0.0), px - x1), dy = max(max(y0 - py, 0.0), py - y1);
        if (dx * dx + dy * dy < R * R - 1e-9) {
            int16_t &f = fixedOwner[k][layer * NC + cellIdx(x, y)];
            if (f == -1) f = owner; else if (f != owner) f = -2;
        }
    }
}

static double distSeg(double px, double py, double ax, double ay, double bx, double by) {
    double vx = bx - ax, vy = by - ay, wx = px - ax, wy = py - ay;
    double l2 = vx * vx + vy * vy; double t = l2 > 0 ? (vx * wx + vy * wy) / l2 : 0; t = max(0.0, min(1.0, t));
    double dx = px - (ax + t * vx), dy = py - (ay + t * vy); return sqrt(dx * dx + dy * dy);
}
static bool pointInPoly(double px, double py) {
    bool in = false; int n = poly.size();
    for (int i = 0, j = n - 1; i < n; j = i++) {
        if (((poly[i].second > py) != (poly[j].second > py)) && (px < (poly[j].first - poly[i].first) * (py - poly[i].second) / (poly[j].second - poly[i].second) + poly[i].first)) in = !in;
    }
    return in;
}

// ------------------------------------------------------------------ routing state
struct Path { vector<array<int, 3>> cells; vector<array<int, 2>> vias; };   // cells (layer, x, y) in order; via positions (x, y)
static vector<vector<Path>> routes;       // per net, list of paths (one per connected pin)
static vector<vector<array<int, 3>>> treeCells;   // per net union of cells (layer,x,y) of all its copper (pads cells, paths, vias on all layers)

static void addDisk(int k, int layer, int cx, int cy, double R, int delta) {
    int r = (int)ceil(R / PITCH);
    for (int dy = -r; dy <= r; dy++) {
        int y = cy + dy; if (y < 0 || y >= NY) continue;
        double h2 = R * R - (dy * PITCH) * (dy * PITCH); if (h2 <= 1e-9) continue;
        int hx = (int)ceil(sqrt(h2) / PITCH - 1e-9);
        // cells with distance < R : |dx*PITCH| < sqrt(h2)
        while (hx > 0 && ((hx * PITCH) * (hx * PITCH) >= h2 - 1e-9)) hx--;
        int xa = max(0, cx - hx), xb = min(NX - 1, cx + hx);
        int16_t *row = &occ[k][layer * NC + cellIdx(0, y)];
        for (int x = xa; x <= xb; x++) row[x] += delta;
    }
}
static void applyPath(int net, const Path &p, int delta) {
    int cls = nets[net].cls;
    // unique cells of the path to avoid double work on corners
    for (auto &c : p.cells) {
        for (int k = 0; k < 5; k++) {
            if (k >= NCL && k != 4) continue;
            addDisk(k, c[0], c[1], c[2], radiusFor(cls, k), delta);
        }
    }
    for (auto &v : p.vias) for (int l = 0; l < NL; l++) for (int k = 0; k < 5; k++) { if (k >= NCL && k != 4) continue; addDisk(k, l, v[0], v[1], radiusFor(4, k), delta); }
}

struct Node { float f; int s; bool operator<(const Node &o) const { return f > o.f; } };
static vector<float> gcost; static vector<int> parentS; static vector<uint32_t> stampA; static uint32_t curStamp = 0;
static vector<uint8_t> isTarget; static vector<uint32_t> targetStamp;
static double PFAC = 0.5; static float HISTINC = 8; static double PGROW = 1.5;
static float STEP = 10, BEND = 5, VIA = 300;
static const float CONFLICT = 60;

static inline int stateIdx(int l, int c, int d) { return (l * NC + c) * 5 + d; }

static bool isPlaneNet(int n) { return nets[n].name == "GND" || nets[n].name == "3V3"; }
static int planeLayerOf(int n) { return nets[n].name == "GND" ? 1 : (nets[n].name == "3V3" ? 2 : -1); }
static bool routeOne(int net, const vector<array<int, 3>> &sources, const vector<array<int, 3>> &targetCells, bool allowViaEnd, Path &out, int &viaCount, double &costOut) {
    // A* from all source cells to any target cell; with allowViaEnd the search also ends when a via down to the In1 layer (a ground plane) can be dropped
    int k = nets[net].cls; bool gndNet = isPlaneNet(net); int planeL = planeLayerOf(net);
    ++curStamp;
    priority_queue<Node> pq;
    int tx0 = 1 << 30, tx1 = -1, ty0 = 1 << 30, ty1 = -1;
    for (auto &t : targetCells) { tx0 = min(tx0, t[1]); tx1 = max(tx1, t[1]); ty0 = min(ty0, t[2]); ty1 = max(ty1, t[2]); }
    for (auto &t : targetCells) targetStamp[t[0] * NC + cellIdx(t[1], t[2])] = curStamp;
    bool noTargets = targetCells.empty();
    auto hfun = [&](int x, int y) -> float {
        if (allowViaEnd || noTargets) return 0;
        int dx = max(max(tx0 - x, 0), x - tx1), dy = max(max(ty0 - y, 0), y - ty1); return (dx + dy) * STEP;
    };
    for (auto &s : sources) {
        int c = cellIdx(s[1], s[2]); int idx = stateIdx(s[0], c, 4);
        int16_t fo = fixedOwner[k][s[0] * NC + c];
        if (fo != -1 && fo != net) continue;
        if (stampA[idx] == curStamp) continue;
        stampA[idx] = curStamp; gcost[idx] = 0; parentS[idx] = -1;
        pq.push({hfun(s[1], s[2]), idx});
    }
    const int DX[4] = {1, -1, 0, 0}, DY[4] = {0, 0, 1, -1};
    int found = -1;
    while (!pq.empty()) {
        Node n = pq.top(); pq.pop();
        int s = n.s; int d = s % 5; int lc = s / 5; int l = lc / NC; int c = lc % NC; int x = c % NX, y = c / NX;
        float g = gcost[s];
        if (n.f > g + hfun(x, y) + 1e-3) continue;
        bool atTarget = (!noTargets && targetStamp[l * NC + c] == curStamp);
        if (allowViaEnd && l == planeL && d == 4 && parentS[s] >= 0) {
            int ps = parentS[s]; int pl = (ps / 5) / NC; if (pl != planeL) atTarget = true;     // arrived by a via move down to the plane layer
        }
        if (atTarget) { found = s; break; }
        for (int m = 0; m < 4 && l != 1 && l != 2; m++) {   // round 2: In1 and In2 are planes, no tracks on them
            int nx = x + DX[m], ny = y + DY[m]; if (nx < 0 || ny < 0 || nx >= NX || ny >= NY) continue;
            int nc = cellIdx(nx, ny);
            int16_t fo = fixedOwner[k][l * NC + nc]; if (fo != -1 && fo != net) continue;
            float cst = STEP * (l == 1 ? 1.6f : 1.0f) + hist[l * NC + nc];
            int oc = occ[k][l * NC + nc]; if (oc > 0) cst += (float)(PFAC * CONFLICT * oc);
            if (d != 4 && d != m) cst += BEND;
            int ns = stateIdx(l, nc, m); float ng = g + cst;
            if (stampA[ns] != curStamp || ng < gcost[ns] - 1e-4) { stampA[ns] = curStamp; gcost[ns] = ng; parentS[ns] = s; pq.push({ng + hfun(nx, ny), ns}); }
        }
        if (!(gndNet ? noViaG[c] : noVia[c])) {
            bool ok = true; for (int ll = 0; ll < NL && ok; ll++) { int16_t fo = fixedOwner[4][ll * NC + c]; if (fo != -1 && fo != net) ok = false; }
            if (ok) {
                float conf = 0; for (int ll = 0; ll < NL; ll++) { int oc = occ[4][ll * NC + c]; if (oc > 0) conf += (float)(PFAC * CONFLICT * oc); }
                for (int nl = 0; nl < NL; nl++) {
                    if (nl == l) continue;
                    if (planeL >= 0) { if (nl != planeL) continue; } else if (nl == 1 || nl == 2) continue;
                    int16_t fo2 = fixedOwner[k][nl * NC + c]; if (fo2 != -1 && fo2 != net) continue;
                    float cst = VIA + conf + hist[nl * NC + c];
                    int ns = stateIdx(nl, c, 4); float ng = g + cst;
                    if (stampA[ns] != curStamp || ng < gcost[ns] - 1e-4) { stampA[ns] = curStamp; gcost[ns] = ng; parentS[ns] = s; pq.push({ng + hfun(x, y), ns}); }
                }
            }
        }
    }
    if (found < 0) return false;
    vector<array<int, 3>> rev; int s = found; costOut = gcost[found];
    while (s >= 0) { int lc = s / 5; rev.push_back({lc / NC, (lc % NC) % NX, (lc % NC) / NX}); s = parentS[s]; }
    reverse(rev.begin(), rev.end());
    out.cells.clear(); out.vias.clear();
    for (size_t i = 0; i < rev.size(); i++) {
        if (i > 0 && rev[i][1] == rev[i - 1][1] && rev[i][2] == rev[i - 1][2] && rev[i][0] != rev[i - 1][0]) out.vias.push_back({rev[i][1], rev[i][2]});
        out.cells.push_back(rev[i]);
    }
    viaCount = out.vias.size();
    return true;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: grid_router in out [seconds] [seed]\n"); return 2; }
    double budget = argc > 3 ? atof(argv[3]) : 600; unsigned seed = argc > 4 ? atoi(argv[4]) : 1; srand(seed);
    if (getenv("VIACOST")) VIA = atof(getenv("VIACOST"));
    if (getenv("HISTINC")) HISTINC = atof(getenv("HISTINC")); if (getenv("PGROW")) PGROW = atof(getenv("PGROW"));
    FILE *f = fopen(argv[1], "r"); if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    char line[512]; int maxnet = -1;
    while (fgets(line, sizeof line, f)) {
        char t = line[0];
        if (t == 'P') sscanf(line + 1, "%lf %lf %lf %d %d", &X0, &Y0, &PITCH, &NX, &NY);
        else if (t == 'W') { sscanf(line + 1, "%d %lf %lf %lf %lf", &NCL, &WIDTH[0], &WIDTH[1], &WIDTH[2], &WIDTH[3]); }
        else if (t == 'C') sscanf(line + 1, "%lf %lf %lf %lf %lf", &CLEAR, &VIAR, &VIADR, &HOLEHOLE, &EDGE);
        else if (t == 'N') { Net n; char nm[200]; sscanf(line + 1, "%d %d %199s", &n.id, &n.cls, nm); n.name = nm; if ((int)nets.size() <= n.id) nets.resize(n.id + 1); nets[n.id] = n; maxnet = max(maxnet, n.id); }
        else if (t == 'R') { Rect r; sscanf(line + 1, "%d %d %lf %lf %lf %lf", &r.mask, &r.net, &r.x0, &r.y0, &r.x1, &r.y1); rects.push_back(r); }
        else if (t == 'O') { Circ c; sscanf(line + 1, "%d %d %lf %lf %lf", &c.mask, &c.net, &c.cx, &c.cy, &c.r); circs.push_back(c); }
        else if (t == 'H') { Hole h; sscanf(line + 1, "%lf %lf %lf %lf", &h.cx, &h.cy, &h.rx, &h.ry); holes.push_back(h); }
        else if (t == 'Q') { Hole h; sscanf(line + 1, "%lf %lf %lf %lf", &h.cx, &h.cy, &h.rx, &h.ry); qholes.push_back(h); }
        else if (t == 'K') { Rect r; sscanf(line + 1, "%d %lf %lf %lf %lf", &r.mask, &r.x0, &r.y0, &r.x1, &r.y1); r.net = -3; keeps.push_back(r); }
        else if (t == 'G') { double x, y; sscanf(line + 1, "%lf %lf", &x, &y); poly.push_back({x, y}); }
        else if (t == 'T') { Term tt; sscanf(line + 1, "%d %d %d %lf %lf %lf %lf", &tt.net, &tt.g, &tt.mask, &tt.x0, &tt.y0, &tt.x1, &tt.y1); terms.push_back(tt); }
    }
    fclose(f);
    NC = NX * NY; int NNET = nets.size();
    for (int k = 0; k < 5; k++) { fixedOwner[k].assign((size_t)NL * NC, -1); occ[k].assign((size_t)NL * NC, 0); }
    hist.assign((size_t)NL * NC, 0.f); noVia.assign(NC, 0); noViaG.assign(NC, 0); inside.assign(NC, 0);
    // outline: outside or too close to the edge is blocked for every class
    for (int y = 0; y < NY; y++) for (int x = 0; x < NX; x++) {
        double px = cwx(x), py = cwy(y); bool in = pointInPoly(px, py); inside[cellIdx(x, y)] = in;
        double de = 1e9; int n = poly.size(); for (int i = 0; i < n; i++) de = min(de, distSeg(px, py, poly[i].first, poly[i].second, poly[(i + 1) % n].first, poly[(i + 1) % n].second));
        for (int k = 0; k < 5; k++) {
            if (k >= NCL && k != 4) continue;
            double w = k == 4 ? VIAR : WIDTH[k] / 2;
            if (!in || de < EDGE + w - 1e-9) for (int l = 0; l < NL; l++) fixedOwner[k][l * NC + cellIdx(x, y)] = -2;
        }
        if (!in || de < EDGE + VIAR) noVia[cellIdx(x, y)] = 1;
    }
    // keepouts: no copper at all
    for (auto &kp : keeps) for (int l = 0; l < NL; l++) if (kp.mask & (1 << l)) for (int k = 0; k < 5; k++) { if (k >= NCL && k != 4) continue; double w = k == 4 ? VIAR : WIDTH[k] / 2; markRectDisk(k, l, -2, kp.x0, kp.y0, kp.x1, kp.y1, w); }
    // fixed copper
    for (auto &r : rects) for (int l = 0; l < NL; l++) if (r.mask & (1 << l)) {
        int own = r.net >= 0 ? r.net : NNET + 7;
        for (int k = 0; k < 5; k++) { if (k >= NCL && k != 4) continue; double w = k == 4 ? VIAR : WIDTH[k] / 2; markRectDisk(k, l, own, r.x0, r.y0, r.x1, r.y1, CLEAR + PADX + w); }
    }
    for (auto &c : circs) for (int l = 0; l < NL; l++) if (c.mask & (1 << l)) {
        int own = c.net >= 0 ? c.net : NNET + 7;
        for (int k = 0; k < 5; k++) { if (k >= NCL && k != 4) continue; double w = k == 4 ? VIAR : WIDTH[k] / 2; markRectDisk(k, l, own, c.cx, c.cy, c.cx, c.cy, c.r + CLEAR + PADX + w); }
    }
    // holes: vias keep hole-to-hole from every hole; tracks keep clearance from the hole wall (hole in copper pads is already in the pad disc)
    for (auto &h : holes) for (int l = 0; l < NL; l++) {
        markRectDisk(4, l, -2, h.cx - h.rx, h.cy - h.ry, h.cx + h.rx, h.cy + h.ry, VIADR + HOLEHOLE);
    }
    // unplated holes: no copper of any kind within hole clearance of the wall (tracks) and hole-to-hole for vias
    for (auto &h : qholes) for (int l = 0; l < NL; l++) {
        markRectDisk(4, l, -2, h.cx - h.rx, h.cy - h.ry, h.cx + h.rx, h.cy + h.ry, VIADR + HOLEHOLE);
        for (int k = 0; k < NCL; k++) markRectDisk(k, l, -2, h.cx - h.rx, h.cy - h.ry, h.cx + h.rx, h.cy + h.ry, CLEAR + WIDTH[k] / 2);
        markRectDisk(4, l, -2, h.cx - h.rx, h.cy - h.ry, h.cx + h.rx, h.cy + h.ry, CLEAR + VIAR);
    }
    // no via near any pad (SMD or PTH): via pad must stay 0.1 mm away from pad copper
    for (auto &r : rects) {
        int ix0 = max(0, (int)floor((r.x0 - VIAR - 0.1 - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((r.x1 + VIAR + 0.1 - X0) / PITCH));
        int iy0 = max(0, (int)floor((r.y0 - VIAR - 0.1 - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((r.y1 + VIAR + 0.1 - Y0) / PITCH));
        for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) {
            double px = cwx(x), py = cwy(y); double dx = max(max(r.x0 - px, 0.0), px - r.x1), dy = max(max(r.y0 - py, 0.0), py - r.y1);
            if (dx * dx + dy * dy < (VIAR + 0.1) * (VIAR + 0.1)) noVia[cellIdx(x, y)] = 1;
        }
    }
    for (auto &t : terms) {
        int ix0 = max(0, (int)floor((t.x0 - VIAR - 0.15 - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((t.x1 + VIAR + 0.15 - X0) / PITCH));
        int iy0 = max(0, (int)floor((t.y0 - VIAR - 0.15 - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((t.y1 + VIAR + 0.15 - Y0) / PITCH));
        for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) {
            double px = cwx(x), py = cwy(y); double dx = max(max(t.x0 - px, 0.0), px - t.x1), dy = max(max(t.y0 - py, 0.0), py - t.y1);
            if (dx * dx + dy * dy < (VIAR + 0.15) * (VIAR + 0.15)) noVia[cellIdx(x, y)] = 1;
        }
    }
    for (auto &c : circs) { int r = (int)ceil((c.r + VIAR + 0.15) / PITCH); int cx = (int)round((c.cx - X0) / PITCH), cy = (int)round((c.cy - Y0) / PITCH);
        for (int y = max(0, cy - r); y <= min(NY - 1, cy + r); y++) for (int x = max(0, cx - r); x <= min(NX - 1, cx + r); x++) { double dx = cwx(x) - c.cx, dy = cwy(y) - c.cy; if (dx * dx + dy * dy < (c.r + VIAR + 0.15) * (c.r + VIAR + 0.15)) noVia[cellIdx(x, y)] = 1; } }
    {   // ground vias: same rule as noVia, but pads of the ground net count only with a 0.02 mm gap
        int gnd = -1, v33 = -1; for (int n = 0; n < NNET; n++) { if (nets[n].name == "GND") gnd = n; if (nets[n].name == "3V3") v33 = n; }
        noViaG = noVia;
        auto clearOwn = [&](double x0, double y0, double x1, double y1) {
            int ix0 = max(0, (int)floor((x0 - VIAR - 0.15 - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((x1 + VIAR + 0.15 - X0) / PITCH));
            int iy0 = max(0, (int)floor((y0 - VIAR - 0.15 - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((y1 + VIAR + 0.15 - Y0) / PITCH));
            for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) { double px = cwx(x), py = cwy(y); double dx = max(max(x0 - px, 0.0), px - x1), dy = max(max(y0 - py, 0.0), py - y1);
                if (dx * dx + dy * dy >= (VIAR + 0.02) * (VIAR + 0.02)) noViaG[cellIdx(x, y)] = 0; }
        };
        // start from the edge rule only, then add every non-ground pad with the full rule and ground pads with the small gap
        for (int y = 0; y < NY; y++) for (int x = 0; x < NX; x++) { double px = cwx(x), py = cwy(y); double de = 1e9; int n = poly.size(); for (int i = 0; i < n; i++) de = min(de, distSeg(px, py, poly[i].first, poly[i].second, poly[(i + 1) % n].first, poly[(i + 1) % n].second)); noViaG[cellIdx(x, y)] = (!inside[cellIdx(x, y)] || de < EDGE + VIAR) ? 1 : 0; }
        auto addPad = [&](double x0, double y0, double x1, double y1, double gap) {
            int ix0 = max(0, (int)floor((x0 - VIAR - gap - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((x1 + VIAR + gap - X0) / PITCH));
            int iy0 = max(0, (int)floor((y0 - VIAR - gap - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((y1 + VIAR + gap - Y0) / PITCH));
            for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) { double px = cwx(x), py = cwy(y); double dx = max(max(x0 - px, 0.0), px - x1), dy = max(max(y0 - py, 0.0), py - y1);
                if (dx * dx + dy * dy < (VIAR + gap) * (VIAR + gap)) noViaG[cellIdx(x, y)] = 1; }
        };
        for (auto &r : rects) addPad(r.x0, r.y0, r.x1, r.y1, (r.net == gnd || r.net == v33) ? 0.02 : 0.1);
        for (auto &c : circs) addPad(c.cx - c.r, c.cy - c.r, c.cx + c.r, c.cy + c.r, (c.net == gnd || c.net == v33) ? 0.02 : 0.1);
        (void)clearOwn;
        for (auto &h : holes) { int ix0 = max(0, (int)floor((h.cx - h.rx - 1.0 - X0) / PITCH)), ix1 = min(NX - 1, (int)ceil((h.cx + h.rx + 1.0 - X0) / PITCH)); int iy0 = max(0, (int)floor((h.cy - h.ry - 1.0 - Y0) / PITCH)), iy1 = min(NY - 1, (int)ceil((h.cy + h.ry + 1.0 - Y0) / PITCH));
            for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) { double px = cwx(x), py = cwy(y); double dx = max(max(h.cx - h.rx - px, 0.0), px - (h.cx + h.rx)), dy = max(max(h.cy - h.ry - py, 0.0), py - (h.cy + h.ry)); if (dx * dx + dy * dy < (VIADR + HOLEHOLE + 0.0) * (VIADR + HOLEHOLE)) noViaG[cellIdx(x, y)] = 1; } }
    }
    // terminals grouped by net
    struct Pin { vector<array<int, 3>> cells; vector<array<int, 3>> cellsAll; };
    vector<vector<Pin>> pins(NNET);
    for (auto &t : terms) {
        if (t.net < 0 || t.net >= NNET) continue;
        Pin p;
        int ix0 = (int)ceil((t.x0 - X0) / PITCH - 1e-9), ix1 = (int)floor((t.x1 - X0) / PITCH + 1e-9), iy0 = (int)ceil((t.y0 - Y0) / PITCH - 1e-9), iy1 = (int)floor((t.y1 - Y0) / PITCH + 1e-9);
        ix0 = max(ix0, 0); iy0 = max(iy0, 0); ix1 = min(ix1, NX - 1); iy1 = min(iy1, NY - 1);
        for (int l = 0; l < NL; l++) if (t.mask & (1 << l)) for (int y = iy0; y <= iy1; y++) for (int x = ix0; x <= ix1; x++) {
            int16_t fo = fixedOwner[nets[t.net].cls][l * NC + cellIdx(x, y)]; if (fo == -1 || fo == t.net) p.cells.push_back({l, x, y});
        }
        if (p.cells.empty()) {   // pad too small for the grid: take the nearest cell to its centre
            int cx = (int)round(((t.x0 + t.x1) / 2 - X0) / PITCH), cy = (int)round(((t.y0 + t.y1) / 2 - Y0) / PITCH); cx = max(0, min(NX - 1, cx)); cy = max(0, min(NY - 1, cy));
            for (int l = 0; l < NL; l++) if (t.mask & (1 << l)) p.cells.push_back({l, cx, cy});
        }
        pins[t.net].push_back(p);
    }
    if (getenv("DUMP")) {   // DUMP="x0,y0,x1,y1,layer,class": ascii map of fixedOwner (. free, # blocked, letter = owner net mod 26)
        double a, b, c, d; int ly, cl; sscanf(getenv("DUMP"), "%lf,%lf,%lf,%lf,%d,%d", &a, &b, &c, &d, &ly, &cl);
        for (double yy = b; yy <= d; yy += PITCH) { for (double xx = a; xx <= c; xx += PITCH) { int x = (int)round((xx - X0) / PITCH), y = (int)round((yy - Y0) / PITCH); int16_t fo = fixedOwner[cl][ly * NC + cellIdx(x, y)]; fputc(fo == -1 ? '.' : fo == -2 ? '#' : 'a' + (fo % 26), stderr); } fputc('\n', stderr); }
    }
    gcost.assign((size_t)NL * NC * 5, 0); parentS.assign((size_t)NL * NC * 5, -1); stampA.assign((size_t)NL * NC * 5, 0); targetStamp.assign((size_t)NL * NC, 0);
    routes.assign(NNET, {}); treeCells.assign(NNET, {});
    auto t0 = chrono::steady_clock::now();
    auto elapsed = [&]() { return chrono::duration<double>(chrono::steady_clock::now() - t0).count(); };
    // net order: by number of pins and spread (small first)
    vector<int> order;
    for (int n = 0; n < NNET; n++) if (pins[n].size() >= 2 || (isPlaneNet(n) && pins[n].size() >= 1)) order.push_back(n);
    auto spread = [&](int n) { double xs0 = 1e9, xs1 = -1e9, ys0 = 1e9, ys1 = -1e9; for (auto &p : pins[n]) { auto &c = p.cells[0]; xs0 = min(xs0, (double)c[1]); xs1 = max(xs1, (double)c[1]); ys0 = min(ys0, (double)c[2]); ys1 = max(ys1, (double)c[2]); } return (xs1 - xs0) + (ys1 - ys0); };
    { vector<double> key(NNET, 0); for (int n : order) key[n] = spread(n) * (seed > 1 ? (0.6 + 0.8 * (rand() / (double)RAND_MAX)) : 1.0); sort(order.begin(), order.end(), [&](int a, int b) { return key[a] < key[b]; }); }
    vector<int> failed(NNET, 0);
    // route one whole net (ripped up before): grows a tree from pin 0
    int iter_dbg = 0;
    auto routeNet = [&](int n) -> bool {
        for (auto &p : routes[n]) applyPath(n, p, -1);
        routes[n].clear();
        bool isGnd = isPlaneNet(n);
        vector<int> remaining; for (size_t i = 1; i < pins[n].size(); i++) remaining.push_back(i);
        vector<array<int, 3>> tree = pins[n][0].cells;
        if (isGnd) { remaining.clear(); for (size_t i = 0; i < pins[n].size(); i++) remaining.push_back(i); tree.clear(); }
        bool all = true; int restart = 0;
        while (!remaining.empty()) {
            int best = -1; double bd = 1e18;
            if (!tree.empty()) {
                for (int i : remaining) { auto &c = pins[n][i].cells[0]; double dm = 1e18; for (auto &t : tree) { double d = abs(t[1] - c[1]) + abs(t[2] - c[2]); if (d < dm) dm = d; if (dm < 1) break; } if (dm < bd) { bd = dm; best = i; } }
            } else best = remaining[0];
            Path pth; int vc = 0; double cost = 0; bool ok;
            if (isGnd) ok = routeOne(n, pins[n][best].cells, tree, true, pth, vc, cost);
            else ok = routeOne(n, tree, pins[n][best].cells, false, pth, vc, cost);
            remaining.erase(find(remaining.begin(), remaining.end(), best));
            if (!ok && iter_dbg == 0) {   // diagnosis: flood fill with the hard rules only
                int k = nets[n].cls; vector<char> seen((size_t)NL * NC, 0); vector<int> q; long cnt = 0; int bx0 = 1 << 30, bx1 = -1, by0 = 1 << 30, by1 = -1; bool viaPossible = false;
                for (auto &c : pins[n][best].cells) { int id = c[0] * NC + cellIdx(c[1], c[2]); if (!seen[id]) { seen[id] = 1; q.push_back(id); } }
                while (!q.empty()) { int id = q.back(); q.pop_back(); cnt++; int l = id / NC, c = id % NC, x = c % NX, y = c / NX; bx0 = min(bx0, x); bx1 = max(bx1, x); by0 = min(by0, y); by1 = max(by1, y);
                    const int DX[4] = {1, -1, 0, 0}, DY[4] = {0, 0, 1, -1};
                    for (int m = 0; m < 4; m++) { int nx = x + DX[m], ny = y + DY[m]; if (nx < 0 || ny < 0 || nx >= NX || ny >= NY) continue; int nid = l * NC + cellIdx(nx, ny); int16_t fo = fixedOwner[k][nid]; if (fo != -1 && fo != n) continue; if (!seen[nid]) { seen[nid] = 1; q.push_back(nid); } }
                    if (!noVia[c]) { bool okv = true; for (int ll = 0; ll < NL && okv; ll++) { int16_t fo = fixedOwner[4][ll * NC + c]; if (fo != -1 && fo != n) okv = false; } if (okv) { viaPossible = true; for (int nl = 0; nl < NL; nl++) { int nid = nl * NC + c; int16_t fo = fixedOwner[k][nid]; if (fo != -1 && fo != n) continue; if (!seen[nid]) { seen[nid] = 1; q.push_back(nid); } } } } }
                fprintf(stderr, "  DIAG net %s pin reachable cells %ld bbox x %.2f..%.2f y %.2f..%.2f via possible %d\n", nets[n].name.c_str(), cnt, cwx(bx0), cwx(bx1), cwy(by0), cwy(by1), (int)viaPossible);
            }
            if (!ok && routes[n].empty() && !isGnd && pins[n].size() > 2 && restart < 6) {   // the start pin may be boxed in: restart the tree from the pin that failed
                restart++; tree = pins[n][best].cells; remaining.clear(); for (size_t i = 0; i < pins[n].size(); i++) if ((int)i != best) remaining.push_back(i); continue;
            }
            if (!ok) { all = false; if (iter_dbg < 3) { auto &c0 = pins[n][best].cells[0]; fprintf(stderr, "  FAIL net %s pin at (%.2f, %.2f) cells %zu\n", nets[n].name.c_str(), cwx(c0[1]), cwy(c0[2]), pins[n][best].cells.size()); } continue; }
            routes[n].push_back(pth);
            for (auto &c : pth.cells) tree.push_back(c);
            for (auto &v : pth.vias) for (int l = 0; l < NL; l++) tree.push_back({l, v[0], v[1]});
            for (auto &c : pins[n][best].cells) tree.push_back(c);
        }
        for (auto &p : routes[n]) applyPath(n, p, +1);
        return all;
    };
    fprintf(stderr, "nets to route %zu, grid %d x %d, %d terminals\n", order.size(), NX, NY, (int)terms.size());
    // GND is handled last as via stubs: here simply routed with the others
    int iter = 0; int conflicts = 1;
    vector<char> bad(NNET, 0); vector<int> confCount(NNET, 0); long bestScore = 1L << 60; auto bestRoutes = routes; int bestConf = 0;
    for (iter = 0; iter < 600 && elapsed() < budget; iter++) {
        PFAC = min(0.4 * pow(PGROW, iter), 3000.0); iter_dbg = iter;
        int nroute = 0;
        vector<int> todo; for (int n : order) if (iter == 0 || bad[n]) todo.push_back(n);
        if (iter > 0) { stable_sort(todo.begin(), todo.end(), [&](int a, int b) { return confCount[a] > confCount[b]; });
            if (iter % 7 == 6) for (size_t i = todo.size(); i > 1; i--) swap(todo[i - 1], todo[rand() % i]); }
        for (int n : todo) { routeNet(n); nroute++; }
        // conflict detection
        conflicts = 0; int unrouted = 0; fill(bad.begin(), bad.end(), 0);
        for (int n : order) {
            // pins connected? count paths
            size_t need = isPlaneNet(n) ? pins[n].size() : pins[n].size() - 1;
            if (routes[n].size() < need) { bad[n] = 1; unrouted++; }
            // overlap with others: remove own, check, add back
            for (auto &p : routes[n]) applyPath(n, p, -1);
            bool conf = false;
            for (auto &p : routes[n]) { for (auto &c : p.cells) if (occ[nets[n].cls][c[0] * NC + cellIdx(c[1], c[2])] > 0) { if (!conf && iter % 10 == 9) fprintf(stderr, "  CONFLICT net %s at layer %d (%.2f, %.2f)\n", nets[n].name.c_str(), c[0], cwx(c[1]), cwy(c[2])); conf = true; hist[c[0] * NC + cellIdx(c[1], c[2])] += HISTINC; }
                for (auto &v : p.vias) for (int l = 0; l < NL; l++) if (occ[4][l * NC + cellIdx(v[0], v[1])] > 0) { conf = true; hist[l * NC + cellIdx(v[0], v[1])] += HISTINC; } }
            for (auto &p : routes[n]) applyPath(n, p, +1);
            if (conf) { bad[n] = 1; conflicts++; confCount[n]++; }
        }
        fprintf(stderr, "iter %d rerouted %d  nets in conflict %d  unrouted %d  t=%.0fs\n", iter, nroute, conflicts, unrouted, elapsed());
        if (iter % 10 == 9 || elapsed() >= budget) { fprintf(stderr, "   in conflict:"); for (int n : order) if (bad[n]) fprintf(stderr, " %s(%d)", nets[n].name.c_str(), confCount[n]); fprintf(stderr, "\n"); }
        { long sc = conflicts * 1000L + unrouted * 100000L; if (sc < bestScore) { bestScore = sc; bestRoutes = routes; bestConf = conflicts; } }
        if (conflicts == 0 && unrouted == 0) break;
    }
    if (bestScore < (1L << 60)) { routes = bestRoutes; conflicts = bestConf; }   // keep the best state seen, not the last
    // write result
    FILE *o = fopen(argv[2], "w");
    int totalUnrouted = 0, totalConf = conflicts;
    for (int n : order) {
        size_t need = isPlaneNet(n) ? pins[n].size() : pins[n].size() - 1;
        if (routes[n].size() < need) { totalUnrouted++; fprintf(o, "UNROUTED %d %s %zu/%zu\n", n, nets[n].name.c_str(), routes[n].size(), need); }
        fprintf(o, "NET %d %s\n", n, nets[n].name.c_str());
        for (auto &p : routes[n]) {
            for (size_t i = 1; i < p.cells.size(); i++) {
                auto &a = p.cells[i - 1], &b = p.cells[i];
                if (a[0] != b[0]) continue;
                fprintf(o, "S %d %.4f %.4f %.4f %.4f\n", a[0], cwx(a[1]), cwy(a[2]), cwx(b[1]), cwy(b[2]));
            }
            for (auto &v : p.vias) fprintf(o, "V %.4f %.4f\n", cwx(v[0]), cwy(v[1]));
        }
    }
    fprintf(o, "SUMMARY iterations %d conflicts %d unrouted %d\n", iter, totalConf, totalUnrouted);
    fclose(o);
    fprintf(stderr, "SUMMARY iterations %d conflicts %d unrouted %d\n", iter, totalConf, totalUnrouted);
    return (totalConf == 0 && totalUnrouted == 0) ? 0 : 1;
}
