## Parameters

You can set the oscillation paramter values and experiment parameters in the parameter setter dropdown at the top of the page. The definitions can be found in the [NuFast paper](https://arxiv.org/pdf/2405.02400v1). 

On top of the parameters needed for oscillation probability calculation, you can also vary the following:
- L/E: this changes the ratio of baseline to neutrino energy. Under the hood it keeps the baseline L constant and changes E to account for the desired L/E ratio.
- L (constant L/E): this changes the baseline while keeping the L/E ratio constant. The L/E ratio is determined from the values of L and E in the parameter setter. Under the hood it changes E to account for the new L value and the current L/E ratio.

## Mass ordering

Mass ordering is currently set via the sign of the mass-squared difference Δm²₃₁. A positive value corresponds to normal ordering, while a negative value corresponds to inverted ordering. A feature to toggle between the two orderings is planned.
## Animation

Enable **Animate** in the animation settings, then choose the parameter and range to vary. Use the slider to inspect individual frames or press **Play** to step through them. **Freeze axes** keeps the same plot limits throughout the animation.

## Overlay

Enable **Overlay** to compare several values of a parameter on one plot.
