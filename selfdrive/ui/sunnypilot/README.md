# Param Watcher (UI)

Param Watcher provides lightweight, panel‑specific parameter caching for UI modules. It ensures parameters are updated only when the panel is open, reducing global param access while keeping the interface responsive.

## Usage in offroad layouts
Initialize in your panel:
```py
  self.param_watcher = ui_state.param_watcher(self)
```

To access parameters in methods such as _update_state:
``` py
  def _update_state(self):
    value = self.param_watcher.get("Foobar")
    flag  = self.param_watcher.get_bool("Boolfar")
```

## Benefits
- Updates at 0.2s intervals, cutting param access by ~4× compared to direct polling in _update_state.
- Keeps offroad panels responsive without visible lag.
- Higher intervals (e.g. 0.5s) are more efficient but introduce noticeable UX delay when toggling values.
