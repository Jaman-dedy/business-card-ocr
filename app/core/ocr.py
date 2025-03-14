import io
import os
import re
from typing import Dict, Any, Tuple, Optional

from google.cloud import vision
from google.cloud.vision_v1 import types

from app.config import GOOGLE_APPLICATION_CREDENTIALS

# Set up credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

class BusinessCardOCR:
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    def process_image(self, image_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process an image using Google Cloud Vision API.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple containing full text and structured contact information
        """
        # Load the image
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()

        # Create image object
        image = types.Image(content=content)

        # Perform text detection
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return "", {}

        # Get full text
        full_text = texts[0].description

        # Extract structured information
        contact_info = self._extract_contact_info(full_text)

        return full_text, contact_info

    def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """
        Extract structured contact information from OCR text.

        Args:
            text: Full OCR text from the business card

        Returns:
            Dictionary containing extracted fields
        """
        lines = text.split('\n')
        contact_info = {
            "name": None,
            "job_title": None,
            "company": None,
            "email": None,
            "phone": None,
            "mobile": None,
            "website": None,
            "address": None,
            "linkedin": None,
            "twitter": None
        }

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact_info["email"] = email_match.group(0)

        # Extract phone numbers
        phone_pattern = r'(\+\d{1,3}[-\.\s]?)?(\(?\d{3}\)?[-\.\s]?)\d{3}[-\.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            for i, match in enumerate(phone_matches):
                if i == 0:
                    contact_info["phone"] = ''.join(match)
                elif i == 1:
                    contact_info["mobile"] = ''.join(match)

        # Extract website
        website_pattern = r'(https?:\/\/)?(www\.)?([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}'
        website_match = re.search(website_pattern, text)
        if website_match:
            contact_info["website"] = website_match.group(0)

        # Heuristic for name and job title (usually first two non-empty lines)
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        if len(non_empty_lines) >= 1:
            contact_info["name"] = non_empty_lines[0]
        if len(non_empty_lines) >= 2:
            contact_info["job_title"] = non_empty_lines[1]

        # Heuristic for company (usually third line or line containing "Inc", "LLC", "Ltd", etc.)
        company_indicators = ["inc", "llc", "ltd", "corporation", "corp", "company", "co"]
        for i, line in enumerate(non_empty_lines):
            if i == 2:  # If it's the third line
                contact_info["company"] = line
                break
            if any(indicator in line.lower() for indicator in company_indicators):
                contact_info["company"] = line
                break

        # Attempt to extract address (heuristic: consecutive lines with numbers, street names, etc.)
        address_parts = []
        address_indicators = ["st", "street", "ave", "avenue", "blvd", "road", "rd", "suite", "ste"]

        for i, line in enumerate(non_empty_lines):
            if any(indicator in line.lower().split() for indicator in address_indicators) or re.search(r'\d{5}(-\d{4})?', line):
                # Look for adjacent lines that might be part of the address
                start_idx = max(0, i-1)
                end_idx = min(len(non_empty_lines), i+2)
                address_parts = non_empty_lines[start_idx:end_idx]
                break

        if address_parts:
            contact_info["address"] = ", ".join(address_parts)

        return contact_info
