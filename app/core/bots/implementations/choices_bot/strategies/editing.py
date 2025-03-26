from abc import ABC
import logging
import os
import time
from typing import Dict, Tuple

from moviepy import (
    ImageClip,
    AudioFileClip,
    TextClip,
    concatenate_videoclips,
    concatenate_audioclips,
    CompositeVideoClip,
    CompositeAudioClip,
)
from moviepy.video.fx import Resize, CrossFadeIn
from moviepy.audio.fx.MultiplyVolume import MultiplyVolume

logger = logging.getLogger('uvicorn.error')

class ChoicesEditingStrategy(ABC):
    """
    Class for video editing strategy that creates 'Would You Rather'-style videos.
    Handles composition of images, text, animations and audio into a final video product.
    """

    # Video configuration
    VIDEO_DIMENSIONS = (1080, 1920)  # (width, height) in pixels
    OUTPUT_DIR = "app/core/assets/tmp/videos"
    OUTPUT_FPS = 24
    OUTPUT_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    PROCESSING_THREADS = 6

    # Text styling
    TEXT_STYLE = {
        'font_size': 60,
        'color': 'white',
        'size': (864, None),  # (width, height) - None means auto
        'text_align': "center",
        'stroke_width': 2,
        'method': 'caption'  # Wrapping method
    }

    PERCENT_STYLE = {
        'font_size': 90,
        'stroke_width': 15,
        'margin': [10, 10]  # [horizontal, vertical]
    }

    # Color palette
    COLORS = {
        "white": '#FFFFFF',
        "black": '#000000',
        "red": '#FF0000',
        "green": '#00FF00',
        "blue": '#0000FF',
    }

    # Animation timing (in seconds)
    ANIMATION_DURATIONS = {
        'slide': 0.3,  # Duration of slide animations
        'fade': 0.2,   # Duration of fade animations
        'tick': 3,     # Duration of tick sound effect
    }

    # Asset paths
    ASSET_PATHS = {
        'background': "app/core/assets/images/wyr-background.png",
        'bg_music': "app/core/assets/music/solitude.mp3",
        'or_sound': "app/core/assets/audios/or.wav",
        'tic_tac': "app/core/assets/audios/tic-tac.mp3",
        'notify': "app/core/assets/audios/notify.mp3",
        'swipe': "app/core/assets/audios/swipe.mp3",
        "sparky": "app/core/assets/fonts/SparkyStones.ttf"
    }

    # Positioning relative to video height (0-1)
    POSITION_FACTORS = {
        'img1_y': 0.035,  # Top image vertical position
        'img2_y': 0.65,   # Bottom image vertical position
        'text1_y': 0.39,  # Top text vertical position
        'text2_y': 0.58   # Bottom text vertical position
    }

    async def _load_assets(self) -> Dict:
        """
        Load all shared assets needed for video editing.
        Returns:
            Dictionary containing preloaded assets (background, audio clips, etc.)
        """
        width, height = self.VIDEO_DIMENSIONS

        return {
            'bg_image': (
                ImageClip(self.ASSET_PATHS['background'])
                .with_effects([Resize(height=height, width=width)])
            ),
            'bg_music': AudioFileClip(self.ASSET_PATHS['bg_music']),
            'or_sound': AudioFileClip(self.ASSET_PATHS['or_sound']),
            'tic_tac': AudioFileClip(self.ASSET_PATHS['tic_tac']),
            'notify': AudioFileClip(self.ASSET_PATHS['notify']),
            'swipe': AudioFileClip(self.ASSET_PATHS['swipe'])
        }

    def _create_image_clip(self, path: str) -> ImageClip:
        """
        Create a standardized ImageClip with consistent settings.
        Args:
            path: File path to the image
        Returns:
            ImageClip with standardized size and settings
        """
        return ImageClip(path).with_effects([Resize(height=600)])

    def _create_text_clip(self, text: str, stroke_color: str) -> TextClip:
        """
        Create a standardized TextClip with consistent styling.
        Args:
            text: The text to display
            stroke_color: Color for text outline
        Returns:
            TextClip with standardized styling
        """
        style = {
            'font': self.ASSET_PATHS['sparky'],
            'text': text,
            'stroke_color': stroke_color,
            **self.TEXT_STYLE
        }
        return TextClip(**style)

    def _create_percent_clip(self, percent: int, is_winner: bool) -> TextClip:
        """
        Create a percentage display TextClip with win/lose styling.
        Args:
            percent: The percentage value to display
            is_winner: Whether this option won
        Returns:
            Styled TextClip showing the percentage
        """
        style = {
            'font': self.ASSET_PATHS['sparky'],
            'text': f"{percent}%",
            'color': self.COLORS['green'] if is_winner else self.COLORS['red'],
            'stroke_color': self.COLORS['white'] if is_winner else self.COLORS['black'],
            **self.PERCENT_STYLE
        }
        return TextClip(**style)

    def _apply_cross_fade_in(
            self, 
            clip: ImageClip, 
            position: Tuple[float, float], 
            duration: float, 
            start: float
        ) -> CompositeVideoClip:
        """
        Apply crossfade animation to a clip.
        Args:
            clip: The clip to animate
            position: (x, y) position tuple
            duration: How long the clip should last
            start: When the animation should begin
        Returns:
            CompositeVideoClip with the animation applied
        """
        clip = clip.with_duration(duration)
        return (
            CompositeVideoClip([
                    clip.with_effects([CrossFadeIn(self.ANIMATION_DURATIONS['fade'])])
                ]
            )
            .with_start(start)
            .with_position(position)
        )

    def _apply_slide_in(
            self, 
            clip: ImageClip, 
            position: Tuple[float, float], 
            side: str, 
            duration: float
        ) -> CompositeVideoClip:
        """
        Apply slide-in animation from outside the screen.
        Args:
            clip: The clip to animate
            position: Target (x, y) position
            side: Which side to slide from ('left' or 'right')
            duration: Total clip duration
        Returns:
            Animated CompositeVideoClip
        """
        width, height = self.VIDEO_DIMENSIONS
        x, y = position

        # Calculate starting position outside the screen
        if side == "left":
            start_pos = (-clip.size[0], y)
        elif side == "right":
            start_pos = (width, y)
        else:
            start_pos = position

        # Animate from starting position to target position
        return clip.with_position(lambda t: (
            start_pos[0] + (x - start_pos[0]) * min(1, t/self.ANIMATION_DURATIONS['slide']),
            y  # Keep same vertical position
        )).with_duration(duration)

    def _apply_slide_out(
            self, 
            clip: ImageClip, 
            position: Tuple[float, float], 
            side: str
        ) -> CompositeVideoClip:
        """
        Apply slide-out animation to outside the screen.
        Args:
            clip: The clip to animate
            position: Current (x, y) position
            side: Which side to slide to ('left' or 'right')
        Returns:
            Animated CompositeVideoClip
        """
        width, height = self.VIDEO_DIMENSIONS
        x, y = position

        # Calculate ending position outside the screen
        if side == "left":
            end_pos = (-clip.size[0], y)
        elif side == "right":
            end_pos = (width, y)
        else:
            end_pos = position

        # Animate from current position to ending position
        return clip.with_position(lambda t: (
            x + (end_pos[0] - x) * min(1, t/self.ANIMATION_DURATIONS['slide']),
            y  # Keep same vertical position
        )).with_duration(self.ANIMATION_DURATIONS['slide'])

    def _calculate_positions(self) -> Dict:
        """
        Calculate all element positions based on video dimensions.
        Returns:
            Dictionary containing:
            - y positions for all elements
            - center_x function for horizontal centering
        """
        width, height = self.VIDEO_DIMENSIONS

        def center_x(clip: ImageClip) -> float:
            """Helper to calculate centered x position for any clip"""
            return (width - clip.size[0]) // 2

        return {
            'img1_y': height * self.POSITION_FACTORS['img1_y'],
            'img2_y': height * self.POSITION_FACTORS['img2_y'],
            'text1_y': height * self.POSITION_FACTORS['text1_y'],
            'text2_y': height * self.POSITION_FACTORS['text2_y'],
            'center_x_func': center_x
        }

    def _create_audio_timeline(
            self, 
            audio1: AudioFileClip, 
            audio2: AudioFileClip, 
            assets: Dict, 
            audio_duration: float,
            audio_duration_and_tick: float,
            audio_final: float
        ) -> AudioFileClip:
        """
        Compose the complete audio timeline for a choice segment.
        Args:
            audio1: First option audio clip
            audio2: Second option audio clip
            assets: Dictionary of shared assets
            audio_duration: Duration of voice + OR sound
            audio_duration_and_tick: Total duration including tick sound
        Returns:
            Concatenated AudioFileClip with all sounds
        """
        tick_audio = assets['tic_tac'].subclipped(0, self.ANIMATION_DURATIONS['tick'])
        swipe_audio = assets['swipe'].subclipped(0.1, assets['swipe'].duration)

        return concatenate_audioclips([
            audio1,
            assets['or_sound'],
            audio2,
            tick_audio.with_start(audio_duration),
            assets['notify'].with_effects([MultiplyVolume(0.5)]).with_start(audio_duration_and_tick),
            swipe_audio.with_effects([MultiplyVolume(2)]).with_start(audio_final)
        ])

    def _process_choice_segment(self, choice: Dict, assets: Dict) -> CompositeVideoClip:
        """
        Process one choice segment with correct timing:
        - Texts disappear when notify starts
        - Percentages stay until notify ends
        - Unified slideout after notify
        """
        pos_data = self._calculate_positions()
        center_x = pos_data['center_x_func']

        opt1, opt2 = choice['option_1'], choice['option_2']
        is_opt1_winner = opt1['percentages'] > opt2['percentages']

        # Load audio and calculate durations
        audio1 = AudioFileClip(opt1['audio_path'])
        audio2 = AudioFileClip(opt2['audio_path'])
        audio_duration = audio1.duration + assets['or_sound'].duration + audio2.duration
        audio_duration_and_tick = audio_duration + self.ANIMATION_DURATIONS['tick']
        total_duration = audio_duration_and_tick + assets['notify'].duration

        # Create all visual elements
        img1 = self._create_image_clip(opt1['image_path'])
        img2 = self._create_image_clip(opt2['image_path'])
        text1 = self._create_text_clip(opt1['text'], self.COLORS["blue"])
        text2 = self._create_text_clip(opt2['text'], self.COLORS["red"])
        percent1 = self._create_percent_clip(opt1['percentages'], is_opt1_winner)
        percent2 = self._create_percent_clip(opt2['percentages'], not is_opt1_winner)

        # Calculate positions
        img1_pos = (center_x(img1), pos_data['img1_y'])
        img2_pos = (center_x(img2), pos_data['img2_y'])
        text1_pos = (center_x(text1), pos_data['text1_y'] - text1.size[1]/2)
        text2_pos = (center_x(text2), pos_data['text2_y'] - text2.size[1]/2)
        percent1_pos = (center_x(percent1), pos_data['text1_y'] - percent1.size[1]/2)
        percent2_pos = (center_x(percent2), pos_data['text2_y'] - percent2.size[1]/2)

        # Create sliding in animations
        img1_slide_in = self._apply_slide_in(img1, img1_pos, "left", total_duration)
        img2_slide_in = self._apply_slide_in(img2, img2_pos, "right", total_duration)
        text1_slide_in = self._apply_slide_in(text1, text1_pos, "left", audio_duration_and_tick)
        text2_slide_in = self._apply_slide_in(text2, text2_pos, "right", audio_duration_and_tick)

        # Percentage fade-in
        percent1 = self._apply_cross_fade_in(
            percent1,
            percent1_pos,
            assets['notify'].duration,
            audio_duration_and_tick
        )
        percent2 = self._apply_cross_fade_in(
            percent2,
            percent2_pos,
            assets['notify'].duration,
            audio_duration_and_tick
        )

        # Slide-out timing (AFTER notify sound completes)
        slide_out_start = total_duration - self.ANIMATION_DURATIONS['slide']

        img1_slide_out = self._apply_slide_out(img1, img1_pos, "right").with_start(slide_out_start)
        img2_slide_out = self._apply_slide_out(img2, img2_pos, "left").with_start(slide_out_start)
        percent1_slide_out = self._apply_slide_out(percent1, percent1_pos, "right").with_start(slide_out_start)
        percent2_slide_out = self._apply_slide_out(percent2, percent2_pos, "left").with_start(slide_out_start)

        # Build audio timeline
        audio_timeline = self._create_audio_timeline(
            audio1,
            audio2,
            assets,
            audio_duration,
            audio_duration_and_tick,
            slide_out_start
        )

        # Compose final clip
        return CompositeVideoClip([
            assets['bg_image'].with_duration(total_duration),
            
            # Images
            img1_slide_in.with_end(slide_out_start),
            img2_slide_in.with_end(slide_out_start),
            
            # Texts
            text1_slide_in,
            text2_slide_in,
            
            # Percentages
            percent1.with_end(slide_out_start),
            percent2.with_end(slide_out_start),
            
            # Unified slide out
            img1_slide_out,
            img2_slide_out,
            percent1_slide_out,
            percent2_slide_out
        ]).with_audio(audio_timeline)

    async def edit(self, content: Dict) -> str:
        """
        Main method to edit the complete video from content.
        Args:
            content: Dictionary containing all choices and options
        Returns:
            Path to the generated video file
        Raises:
            Exception: If any error occurs during video processing
        """
        try:
            assets = await self._load_assets()
            final_clips = []
            temp_files_to_delete = []
            
            for choice in content['choices']:
                temp_files_to_delete.extend([
                    choice['option_1']['image_path'], choice['option_1']['audio_path'],
                    choice['option_2']['image_path'], choice['option_2']['audio_path']
                ])

                segment = self._process_choice_segment(choice, assets)
                final_clips.append(segment)
            
            # Concatenate all segments
            final_video = concatenate_videoclips(final_clips)
            
            # Add background music
            bg_music = assets['bg_music'].with_effects([MultiplyVolume(0.1)])
            final_audio = CompositeAudioClip([bg_music, final_video.audio])
            final_video = final_video.with_audio(final_audio)
            
            # Save the video
            output_path = f"{self.OUTPUT_DIR}/final_{int(time.time())}.mp4"

            final_video.write_videofile(
                output_path,
                fps=self.OUTPUT_FPS,
                codec=self.OUTPUT_CODEC,
                audio_codec=self.AUDIO_CODEC,
                threads=self.PROCESSING_THREADS
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
