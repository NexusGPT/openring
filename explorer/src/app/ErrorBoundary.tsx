import { Component, type ReactNode } from 'react'
import { testId } from '../contract'

/** A screen that throws must not blank the page: the tab bar and the stage stay, the panel says so. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  override state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  override render() {
    if (!this.state.failed) return this.props.children
    return (
      <div className="placeholder" role="alert" data-testid={testId('app', 'screen-failed')}>
        <h1 className="display">This screen failed to draw.</h1>
        <p className="muted">Reload the page. The other screens are not affected.</p>
      </div>
    )
  }
}
