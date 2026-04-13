try:
    from .spiral_plugin import SpiralGeneratorPlugin
    plugin = SpiralGeneratorPlugin()
    plugin.register()
except Exception as e:
    import traceback
    traceback.print_exc()
