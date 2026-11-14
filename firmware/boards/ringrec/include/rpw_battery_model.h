/*
 * rpw_battery_model.h: the cell model for the fuel gauge of the ring (software step 7), the header that
 * modules/ring_power/src/rpw_hw_real.c includes by this name and reads as `battery_model`.
 *
 * NOT THE RING'S CELL: A STAND-IN. ring_battery_model_20mAh.inc is a byte-for-byte copy of the nRF Connect SDK v3.4.2
 * file nrf/samples/pmic/native/npm13xx_fuel_gauge/src/battery_model_20mAh.inc (sha256 d462a345...b3a37, model name
 * "LP18l917"), the model Nordic's own sample uses with the nPM1304 evaluation kit. It is a 20 mAh lithium cell, inside
 * the ring's measured range (17.6 to 31.9 mAh, design/firmware.md 8.1), but it is not a model of the ring's cell:
 * design/firmware.md 8.3 (l.930) requires a model of the actual cells made with nPM PowerUP; one model per ring size or
 * one for all is open (section 10.5, item 4). Replace the .inc when that model exists.
 */
#ifndef RPW_BATTERY_MODEL_H_
#define RPW_BATTERY_MODEL_H_

#include <nrf_fuel_gauge.h>

static const struct battery_model battery_model = {
#include "ring_battery_model_20mAh.inc"
};

#endif /* RPW_BATTERY_MODEL_H_ */
