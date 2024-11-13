bl_info = {
    "name": "Audio Exporter",
    "description": "Export audio with custom options, channel mapping, and speaker arrangements.",
    "author": "Dinesh",
    "version": (1, 0, 0),
    "blender": (2, 8, 0),
    "category": "Sequencer",
    "location": "Sequencer > AudioExport(Tab)",
}

import bpy
import os
import time

# Operator for exporting audio file
class ExportAudioOperator(bpy.types.Operator):
    bl_idname = "sequencer.export_audio_file"
    bl_label = "Export Audio File"
    bl_icon = 'EXPORT'
    bl_description = "Exports selected audio strips with custom settings"

    def execute(self, context):
        scene = context.scene
        
        # Get the export mode (separate or combined)
        export_mode = scene.export_audio_mode

        # Store the original mute states of the strips
        original_mute_states = {}
        for strip in scene.sequence_editor.sequences_all:
            if strip.type == 'SOUND':
                original_mute_states[strip.channel] = strip.mute
        
        # Get the selected audio strips
        selected_strips = [strip for strip in scene.sequence_editor.sequences_all if strip.type == 'SOUND' and strip.select]
        
        if not selected_strips:
            self.report({'WARNING'}, "No audio strips selected.")
            return {'CANCELLED'}

        # Verify that the output path exists
        if not os.path.isdir(scene.export_audio_output_path):
            self.report({'ERROR'}, "Invalid output path. Please set a valid directory.")
            return {'CANCELLED'}

        # Helper function to check if a file exists and append a unique counter if necessary
        def check_and_generate_filename(file_path):
            base_name, ext = os.path.splitext(file_path)
            counter = 1
            # Loop to ensure the file name is unique
            while os.path.exists(file_path):
                file_path = f"{base_name}_{counter}{ext}"
                counter += 1
            return file_path

        # Process based on export mode
        if export_mode == 'SEPARATE':
            # Auto-numbering counter
            counter = 1
            for strip in selected_strips:
                output_path = scene.export_audio_output_path
                audio_container = scene.export_audio_container
                file_name = f"{strip.name}_{counter}.{audio_container.lower()}"
                output_file_path = os.path.join(output_path, file_name)

                # Check if file exists and modify the filename if necessary
                output_file_path = check_and_generate_filename(output_file_path)  # Specific comment line for file existence check

                counter += 1  # Increment counter for each separate file

                # Set sample rate and bit rate
                sample_rate = scene.export_audio_sample_rate
                bit_rate = scene.export_audio_bit_rate
                
                # Set render Properties
                scene.render.image_settings.file_format = 'FFMPEG'
                scene.render.ffmpeg.audio_codec = audio_container
                scene.render.ffmpeg.audio_bitrate = bit_rate

                # Delete existing output file if it exists
                if os.path.exists(output_file_path):
                    os.remove(output_file_path)

                # Mute all other strips and set frame range for export
                for other_strip in scene.sequence_editor.sequences_all:
                    if other_strip != strip and other_strip.type == 'SOUND':
                        other_strip.mute = True
                    else:
                        other_strip.mute = False

                # Set the frame range for rendering based on the selected strip's duration
                scene.frame_start = int(strip.frame_start)  # Convert to int
                scene.frame_end = int(strip.frame_final_end)  # Use frame_final_end for the correct end frame

                # Render audio strip
                bpy.ops.sound.mixdown(
                    filepath=output_file_path,
                    codec=audio_container,
                    container=audio_container,
                )         

        elif export_mode == 'COMBINED':
            combined_file_name = "Combined_Audio." + scene.export_audio_container.lower()
            output_file_path = os.path.join(scene.export_audio_output_path, combined_file_name)

            # Check if file exists and modify the filename if necessary
            output_file_path = check_and_generate_filename(output_file_path)  # Specific comment line for file existence check

            sample_rate = scene.export_audio_sample_rate
            bit_rate = scene.export_audio_bit_rate

            scene.render.image_settings.file_format = 'FFMPEG'
            scene.render.ffmpeg.audio_codec = scene.export_audio_container
            scene.render.ffmpeg.audio_bitrate = bit_rate

            if os.path.exists(output_file_path):
                os.remove(output_file_path)

            for strip in scene.sequence_editor.sequences_all:
                if strip.type == 'SOUND' and strip.select:
                    strip.mute = False
                else:
                    strip.mute = True

            combined_start = min(int(strip.frame_start) for strip in selected_strips)
            combined_end = max(int(strip.frame_final_end) for strip in selected_strips)

            scene.frame_start = combined_start
            scene.frame_end = combined_end      

            bpy.ops.sound.mixdown(
                filepath=output_file_path,
                codec=scene.export_audio_container,
                container=scene.export_audio_container,
            )

        # Restore the original mute states of the strips
        for strip in scene.sequence_editor.sequences_all:
            if strip.type == 'SOUND':
                strip.mute = original_mute_states.get(strip.channel, False)

        self.report({'INFO'}, "Audio Files Exported Successfully!")
        return {'FINISHED'}

# Panel for the Audio Export tab with Channel Mapping
class AudioExportPanel(bpy.types.Panel):
    bl_idname = "SEQUENCER_PT_audio_export_panel"
    bl_label = "Audio Properties"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Audio Export'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # File output path
        layout.label(text="Output Path:")
        row = layout.row(align=True)
        row.prop(context.scene, "export_audio_output_path", text="", icon='FILE_FOLDER')
        
        # Audio container dropdown
        layout.label(text="Audio Container:")
        row = layout.row(align=True)
        row.prop(context.scene, "export_audio_container", text="", icon='SOUND')
        
        # Sample Rate
        layout.label(text="Sample Rate (Hz):")
        layout.prop(context.scene, "export_audio_sample_rate", text="")
        
        # Bit Rate
        layout.label(text="Bit Rate (kbps):")
        layout.prop(context.scene, "export_audio_bit_rate", text="")

        # Export Mode: Separate or Combined
        layout.label(text="Export Mode:")
        row = layout.row(align=True)
        row.prop(context.scene, "export_audio_mode", text="")

        # Channel Mapping section (only show when 'COMBINED' is selected)
        if scene.export_audio_mode == 'COMBINED':
            layout.separator()
            
            # Speaker Arrangement Dropdown (Stereo, 5.1, 7.1)
            layout.label(text="Speaker Arrangement:")
            row = layout.row(align=True)
            row.prop(context.scene, "export_audio_speaker_arrangement", text="", icon='SPEAKER')
            
            # Advanced Channel Mapping Options
            layout.label(text="Advanced Channel Mapping:")
            for i in range(8):  # Max 8 channels
                row = layout.row(align=True)
                row.prop(context.scene, f"export_audio_channel_{i+1}", text=f"{i+1} Channel ")

        # Export Button
        layout.operator("sequencer.export_audio_file", text="Export Audio", icon='EXPORT')

# Register the classes
classes = [
    ExportAudioOperator,
    AudioExportPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Define properties directly with bpy.props
    bpy.types.Scene.export_audio_output_path = bpy.props.StringProperty(
        name="Output Path",
        default="",
        subtype='DIR_PATH',
    )
    bpy.types.Scene.export_audio_sample_rate = bpy.props.IntProperty(
        name="Sample Rate",
        default=44100,
        min=1,
    )
    bpy.types.Scene.export_audio_bit_rate = bpy.props.IntProperty(
        name="Bit Rate",
        default=192,
        min=1,

    )
    bpy.types.Scene.export_audio_container = bpy.props.EnumProperty(
        name="Audio Container",
        items=[
            ('MP3', 'MP3', 'MP3 audio format'),
            ('FLAC', 'FLAC', 'FLAC audio format'),
            ('AC3', 'AC3', 'AC3 audio format'),
            ('MP2', 'MP2', 'MP2 audio format'),
        ],
        default='MP3',
    )
    bpy.types.Scene.export_audio_mode = bpy.props.EnumProperty(
        name="Export Mode",
        items=[
            ('SEPARATE', 'Separate Files', 'Export each audio strip separately'),
            ('COMBINED', 'Combined File', 'Combine selected audio strips into one file'),
        ],
        default='SEPARATE',
    )
    bpy.types.Scene.export_audio_speaker_arrangement = bpy.props.EnumProperty(
        name="Speaker Arrangement",
        items=[
            ('STEREO', 'Stereo', '2 channels (Left, Right)'),
            ('SURROUND_5_1', '5.1 Surround', '6 channels (Front Left, Front Right, Center, Subwoofer, Rear Left, Rear Right)'),
            ('SURROUND_7_1', '7.1 Surround', '8 channels (Front Left, Front Right, Center, Subwoofer, Rear Left, Rear Right, Side Left, Side Right)'),
        ],
        default='STEREO',
    )
    
    # Default different types for each channel (from 1 to 8)
    default_speaker_mapping = ['LEFT', 'RIGHT', 'CENTER', 'SUBWOOFER', 'REAR_LEFT', 'REAR_RIGHT', 'SIDE_LEFT', 'SIDE_RIGHT']
    for i, speaker_type in enumerate(default_speaker_mapping):
        setattr(bpy.types.Scene, f"export_audio_channel_{i+1}", bpy.props.EnumProperty(
            name=f"Channel {i+1}",
            items=[
                ('LEFT', 'Left', 'Left speaker'),
                ('RIGHT', 'Right', 'Right speaker'),
                ('CENTER', 'Center', 'Center speaker'),
                ('SUBWOOFER', 'Subwoofer', 'Subwoofer speaker'),
                ('REAR_LEFT', 'Rear Left', 'Rear Left speaker'),
                ('REAR_RIGHT', 'Rear Right', 'Rear Right speaker'),
                ('SIDE_LEFT', 'Side Left', 'Side Left speaker'),
                ('SIDE_RIGHT', 'Side Right', 'Side Right speaker'),
            ],
            default=speaker_type,
        ))
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.export_audio_output_path
    del bpy.types.Scene.export_audio_sample_rate
    del bpy.types.Scene.export_audio_bit_rate
    del bpy.types.Scene.export_audio_container
    del bpy.types.Scene.export_audio_mode
    del bpy.types.Scene.export_audio_speaker_arrangement
    for i in range(8):
        delattr(bpy.types.Scene, f"export_audio_channel_{i+1}")

if __name__ == "__main__":
    register()
