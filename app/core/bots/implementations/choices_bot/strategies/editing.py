from abc import ABC
import logging
import os
import time

from moviepy.editor import *
from moviepy.audio.fx.volumex import volumex
from moviepy.config import change_settings

# Global settings
change_settings({
    "IMAGEMAGICK_BINARY": 
        "/usr/bin/convert" if os.name != "nt" else 
        "C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\convert.exe"
})

logger = logging.getLogger('uvicorn.error')

class ChoicesEditingStrategy(ABC):
    # Constants
    VIDEO_DIMENSIONS = (1080, 1920)
    TEXT_STYLE = {
        'fontsize': 50,
        'color': 'white',
        'font': 'Comic Sans MS',
        'stroke_color': 'white',
        'stroke_width': 5,
        'method': 'caption'
    }
    PERCENT_STYLE = {
        'fontsize': 100,
        'color': 'white',
        'font': 'Comic Sans MS',
        'stroke_color': 'white',
        'stroke_width': 4
    }

    # Assets paths
    ASSET_PATHS = {
        'background': "app/core/assets/images/wyr-background.png",
        'bg_music': "app/core/assets/music/solitude.mp3",
        'or_sound': "app/core/assets/audios/or.wav",
        'tic_tac': "app/core/assets/audios/tic-tac.mp3",
        'notify': "app/core/assets/audios/notify.mp3"
    }

    OUTPUT_DIR = "app/core/assets/tmp/videos"

    async def _load_assets(self):
        """Load all shared assets"""
        W, H = self.VIDEO_DIMENSIONS

        return {
            'bg_image': ImageClip(self.ASSET_PATHS['background']).resize((W, H)),
            'bg_music': AudioFileClip(self.ASSET_PATHS['bg_music']),
            'or_sound': AudioFileClip(self.ASSET_PATHS['or_sound']),
            'tic_tac': AudioFileClip(self.ASSET_PATHS['tic_tac']),
            'notify': AudioFileClip(self.ASSET_PATHS['notify'])
        }
    
    def _create_image_clip(self, path, position_y):
        """Create a ImageClip with consistent settings"""
        return ImageClip(
            path
        ).resize(height=600)\
        .set_position(("center", position_y))

    def _create_text_clip(self, text, position_y, duration, size_ratio=0.8):
        """Create a TextClip with consistent settings"""
        W, H = self.VIDEO_DIMENSIONS
        return TextClip(
            text,
            size=(W * size_ratio, None),
            **self.TEXT_STYLE
        ).set_position(("center", position_y)).set_duration(duration)

    def _create_percent_clip(self, percent, position):
        """Create a TextClip to display percentages"""
        return TextClip(
            f"{percent}%",
            **self.PERCENT_STYLE
        ).set_position(position)

    def _process_choice_segment(self, choice, assets):
        """Process an individual choice segment"""
        W, H = self.VIDEO_DIMENSIONS
        opt1, opt2 = choice['option_1'], choice['option_2']

        # Positioning settings
        positions = {
            'img1_y': 0.05 * H,
            'img2_y': 0.65 * H,
            'text1_y': 0.38 * H,
            'text2_y': 0.55 * H
        }

        # Duration settings
        durations = {
            'tick': 3,
            'notify': assets['notify'].duration,
            'or': assets['or_sound'].duration
        }

        # Load choice-specific images and audio
        img1 = self._create_image_clip(opt1['image_path'], positions['img1_y'])
        img2 = self._create_image_clip(opt2['image_path'], positions['img2_y'])

        audio1 = AudioFileClip(opt1['audio_path'])
        audio2 = AudioFileClip(opt2['audio_path'])

        # Create text elements
        audio_duration = audio1.duration + durations['or'] + audio2.duration
        audio_duration_and_tick = audio_duration + durations['tick']
        total_duration = audio_duration_and_tick + durations['notify']

        text1 = self._create_text_clip(opt1['text'], positions['text1_y'], audio_duration_and_tick)
        text2 = self._create_text_clip(opt2['text'], positions['text2_y'], audio_duration_and_tick)

        # Create percentage elements
        percent_duration = durations['notify']
        percent1 = self._create_percent_clip(opt1['percentages'], text1.pos)
        percent2 = self._create_percent_clip(opt2['percentages'], text2.pos)

        # Configure element timing
        percent_start = audio_duration_and_tick
        percent1 = percent1.set_start(percent_start).set_duration(percent_duration)
        percent2 = percent2.set_start(percent_start).set_duration(percent_duration)

        # Build audio timeline
        tick_audio = assets['tic_tac'].subclip(0, durations['tick'])
        audio_timeline = concatenate_audioclips([
            audio1,
            assets['or_sound'],
            audio2,
            tick_audio.set_start(audio_duration),
            assets['notify'].set_start(audio_duration_and_tick)
        ])

        # Compose the complete clip
        return CompositeVideoClip([
            assets['bg_image'].set_duration(total_duration),
            img1.set_duration(total_duration),
            img2.set_duration(total_duration),
            text1,
            text2,
            percent1,
            percent2
        ]).set_audio(audio_timeline)

    async def edit(self, content):
        try:
            assets = await self._load_assets()
            final_clips = []

            # List to store all temporary files that need to be deleted
            temp_files_to_delete = []

            for choice in content['choices']:
                # Adds the paths of images and audios to the exclusion list
                temp_files_to_delete.extend([
                    choice['option_1']['image_path'], choice['option_1']['audio_path'],
                    choice['option_2']['image_path'], choice['option_2']['audio_path']
                ])

                segment = self._process_choice_segment(choice, assets)
                final_clips.append(segment)

            # Concatenate all segments
            final_video = concatenate_videoclips(final_clips)

            # Add background music
            bg_music = assets['bg_music'].fx(volumex, 0.1)
            final_audio = CompositeAudioClip([bg_music, final_video.audio])
            final_video = final_video.set_audio(final_audio)

            # Save the video
            output_path = f"{self.OUTPUT_DIR}/final_{int(time.time())}.mp4"

            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                threads=4
            )

            # Close all clips to free up resources
            final_video.close()
            for clip in final_clips:
                clip.close()

            # Deletes temporary files
            for file_path in temp_files_to_delete:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.error(f"Error deleting temporary file {file_path}: {str(e)}")

            return output_path

        except Exception as e:
            logger.error(f"Error in video editing: {str(e)}")
            raise
