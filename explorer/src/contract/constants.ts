// The one place thresholds, counts and ports are written is contract/schema/constants.json.
// This file only types it for the app.
import constants from '../../contract/schema/constants.json' with { type: 'json' }

export const HOST: string = constants.HOST
export const APP_PORT: number = constants.APP_PORT
export const JOURNEY_PORT: number = constants.JOURNEY_PORT
export const GLB_MAX_MB: number = constants.GLB_MAX_MB
export const EXPLODE_MIN_GAP_MM: number = constants.EXPLODE_MIN_GAP_MM
export const BOARD_SIDE_MM: number = constants.BOARD_SIDE_MM
export const NOTE_WHAT_WORDS: number = constants.NOTE_WHAT_WORDS
export const NOTE_WHY_WORDS: number = constants.NOTE_WHY_WORDS
export const PANEL_MAX_WORDS: number = constants.PANEL_MAX_WORDS
