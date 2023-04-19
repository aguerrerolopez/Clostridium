/**
 * Wait
 * @param  ms Delay in milliseconds
 * @return    Callback when done
 */
export function wait(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
}
