"""
Image Processor - Image Preprocessing and Enhancement

This module provides image preprocessing capabilities to optimize receipt images
for OCR and AI vision analysis.
"""

import logging
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional
from pathlib import Path
import io

from .config import Config

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Image preprocessing and enhancement for receipt processing."""
    
    def __init__(self, config: Config):
        """Initialize image processor."""
        self.config = config
        self.max_width = 1920
        self.max_height = 1920
        self.min_width = 400
        self.min_height = 400
        
        logger.info("Image processor initialized")
    
    def preprocess(self, image_path: str) -> str:
        """
        Preprocess an image for optimal OCR and AI analysis.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the preprocessed image
        """
        try:
            # Load image
            image = self._load_image(image_path)
            
            # Apply preprocessing pipeline
            processed_image = self._preprocessing_pipeline(image)
            
            # Save processed image
            output_path = self._get_output_path(image_path)
            self._save_image(processed_image, output_path)
            
            logger.debug(f"Image preprocessed: {image_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Image preprocessing failed for {image_path}: {str(e)}")
            # Return original path if preprocessing fails
            return image_path
    
    def _load_image(self, image_path: str) -> np.ndarray:
        """Load image using OpenCV."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        return image
    
    def _preprocessing_pipeline(self, image: np.ndarray) -> np.ndarray:
        """Apply complete preprocessing pipeline."""
        
        # Step 1: Resize if necessary
        image = self._resize_image(image)
        
        # Step 2: Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Step 3: Noise reduction
        denoised = self._denoise_image(gray)
        
        # Step 4: Enhance contrast
        enhanced = self._enhance_contrast(denoised)
        
        # Step 5: Correct perspective (if needed)
        corrected = self._correct_perspective(enhanced)
        
        # Step 6: Improve sharpness
        sharpened = self._sharpen_image(corrected)
        
        # Step 7: Final cleanup
        cleaned = self._cleanup_image(sharpened)
        
        return cleaned
    
    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image to optimal dimensions."""
        height, width = image.shape[:2]
        
        # Check if resizing is needed
        if (width <= self.max_width and height <= self.max_height and 
            width >= self.min_width and height >= self.min_height):
            return image
        
        # Calculate new dimensions
        if width > self.max_width or height > self.max_height:
            # Scale down
            scale = min(self.max_width / width, self.max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
        else:
            # Scale up
            scale = max(self.min_width / width, self.min_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
        
        # Resize using high-quality interpolation
        if scale > 1:
            interpolation = cv2.INTER_CUBIC
        else:
            interpolation = cv2.INTER_AREA
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=interpolation)
        logger.debug(f"Image resized from {width}x{height} to {new_width}x{new_height}")
        
        return resized
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Remove noise from the image."""
        # Use Non-local Means Denoising
        denoised = cv2.fastNlMeansDenoising(image, None, 10, 7, 21)
        return denoised
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE."""
        # Create CLAHE object
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        
        # Apply CLAHE
        enhanced = clahe.apply(image)
        
        return enhanced
    
    def _correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Attempt to correct perspective distortion."""
        try:
            # Find edges
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour
            for contour in sorted(contours, key=cv2.contourArea, reverse=True):
                # Approximate contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # If we found a quadrilateral that's large enough
                if len(approx) == 4 and cv2.contourArea(approx) > image.shape[0] * image.shape[1] * 0.1:
                    # Apply perspective correction
                    return self._apply_perspective_transform(image, approx)
            
            # If no good quadrilateral found, return original
            return image
            
        except Exception as e:
            logger.debug(f"Perspective correction failed: {str(e)}")
            return image
    
    def _apply_perspective_transform(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """Apply perspective transformation to correct document orientation."""
        # Order the corners: top-left, top-right, bottom-right, bottom-left
        corners = corners.reshape((4, 2))
        
        # Calculate the center
        center = np.mean(corners, axis=0)
        
        # Sort corners by angle from center
        def angle_from_center(point):
            return np.arctan2(point[1] - center[1], point[0] - center[0])
        
        corners = sorted(corners, key=angle_from_center)
        
        # Determine output dimensions
        width = int(max(
            np.linalg.norm(corners[1] - corners[0]),
            np.linalg.norm(corners[2] - corners[3])
        ))
        height = int(max(
            np.linalg.norm(corners[2] - corners[1]),
            np.linalg.norm(corners[3] - corners[0])
        ))
        
        # Define destination points
        dst_points = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype=np.float32)
        
        # Calculate perspective transform matrix
        src_points = np.array(corners, dtype=np.float32)
        matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        
        # Apply transformation
        corrected = cv2.warpPerspective(image, matrix, (width, height))
        
        return corrected
    
    def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Apply sharpening filter to improve text clarity."""
        # Unsharp mask
        gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        
        return sharpened
    
    def _cleanup_image(self, image: np.ndarray) -> np.ndarray:
        """Final cleanup and optimization."""
        # Apply morphological operations to clean up small artifacts
        kernel = np.ones((2, 2), np.uint8)
        
        # Remove small noise
        cleaned = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        
        # Fill small holes
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _get_output_path(self, input_path: str) -> str:
        """Generate output path for processed image."""
        path = Path(input_path)
        output_path = path.parent / f"{path.stem}_processed{path.suffix}"
        return str(output_path)
    
    def _save_image(self, image: np.ndarray, output_path: str):
        """Save processed image."""
        cv2.imwrite(output_path, image)
    
    def enhance_for_ocr(self, image_path: str) -> str:
        """
        Enhance image specifically for OCR processing.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Path to OCR-optimized image
        """
        try:
            image = self._load_image(image_path)
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply aggressive preprocessing for OCR
            processed = self._ocr_preprocessing(gray)
            
            # Save OCR-optimized image
            output_path = self._get_ocr_output_path(image_path)
            cv2.imwrite(output_path, processed)
            
            return output_path
            
        except Exception as e:
            logger.error(f"OCR enhancement failed for {image_path}: {str(e)}")
            return image_path
    
    def _ocr_preprocessing(self, image: np.ndarray) -> np.ndarray:
        """Aggressive preprocessing specifically for OCR."""
        
        # 1. Resize for optimal OCR (tesseract works best with larger images)
        height, width = image.shape
        if height < 800:
            scale = 800 / height
            new_width = int(width * scale)
            image = cv2.resize(image, (new_width, 800), interpolation=cv2.INTER_CUBIC)
        
        # 2. Denoise
        denoised = cv2.fastNlMeansDenoising(image)
        
        # 3. Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 4. Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 5. Morphological operations to connect text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def _get_ocr_output_path(self, input_path: str) -> str:
        """Generate output path for OCR-optimized image."""
        path = Path(input_path)
        output_path = path.parent / f"{path.stem}_ocr{path.suffix}"
        return str(output_path)
    
    def convert_to_supported_format(self, image_path: str, target_format: str = 'jpg') -> str:
        """
        Convert image to a supported format.
        
        Args:
            image_path: Path to input image
            target_format: Target format (jpg, png, etc.)
            
        Returns:
            Path to converted image
        """
        try:
            # Load with PIL for format conversion
            pil_image = Image.open(image_path)
            
            # Convert to RGB if necessary (for JPEG)
            if target_format.lower() in ['jpg', 'jpeg'] and pil_image.mode in ['RGBA', 'P']:
                pil_image = pil_image.convert('RGB')
            
            # Generate output path
            path = Path(image_path)
            output_path = path.parent / f"{path.stem}.{target_format.lower()}"
            
            # Save in target format
            pil_image.save(output_path, format=target_format.upper())
            
            logger.debug(f"Image converted: {image_path} -> {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Format conversion failed for {image_path}: {str(e)}")
            return image_path
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get detailed information about an image.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Dictionary with image information
        """
        try:
            # Load with PIL for metadata
            pil_image = Image.open(image_path)
            
            # Load with OpenCV for additional analysis
            cv_image = cv2.imread(image_path)
            
            info = {
                'path': image_path,
                'size': pil_image.size,  # (width, height)
                'mode': pil_image.mode,
                'format': pil_image.format,
                'file_size': Path(image_path).stat().st_size,
                'channels': len(cv_image.shape) if cv_image is not None else None,
                'dtype': str(cv_image.dtype) if cv_image is not None else None
            }
            
            # Add EXIF data if available
            if hasattr(pil_image, '_getexif') and pil_image._getexif():
                info['has_exif'] = True
            else:
                info['has_exif'] = False
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get image info for {image_path}: {str(e)}")
            return {'path': image_path, 'error': str(e)}
