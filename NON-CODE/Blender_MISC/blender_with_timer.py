import bpy

class SimpleTimerOperator(bpy.types.Operator):
    bl_idname = "wm.simple_timer_operator"
    bl_label = "Simple Timer Operator"
    
    _timer = None

    def modal(self, context, event):
        if event.type == 'TIMER':
            # This is where you can call the function to send data over the socket
            send_bone_data()
        
        # You can add a condition here to stop the timer when needed
        # if some_condition:
        #     self.cancel(context)
        #     return {'CANCELLED'}

        return {'PASS_THROUGH'}
    
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)  # Call every 1 second
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

# Registering the operator
bpy.utils.register_class(SimpleTimerOperator)

# To start the timer, you can call:
bpy.ops.wm.simple_timer_operator()
