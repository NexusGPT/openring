// The case lid: rotate a node about the hinge from its rest pose. Hinge point and axis are design coordinates.
import * as THREE from 'three'
import { toThree } from './layers'

/** Returns the node's rest world matrix (taken on the first call, pass it back on the next). */
export function rotateAbout(obj: THREE.Object3D, rest: THREE.Matrix4 | null, point: { x: number; y: number; z: number }, axis: { x: number; y: number; z: number }, deg: number): THREE.Matrix4 {
  obj.updateWorldMatrix(true, false)
  const rest0 = rest ?? obj.matrixWorld.clone()
  const pivot = toThree(point)
  const rot = new THREE.Matrix4()
    .makeTranslation(pivot.x, pivot.y, pivot.z)
    .multiply(new THREE.Matrix4().makeRotationAxis(toThree(axis).normalize(), THREE.MathUtils.degToRad(deg)))
    .multiply(new THREE.Matrix4().makeTranslation(-pivot.x, -pivot.y, -pivot.z))
  const parentInv = (obj.parent?.matrixWorld ?? new THREE.Matrix4()).clone().invert()
  parentInv.multiply(rot).multiply(rest0).decompose(obj.position, obj.quaternion, obj.scale)
  obj.updateMatrixWorld(true)
  return rest0
}
