import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
from typing import Dict, List
import time


class AustralianEducationDataCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Data storage
        self.university_data = {}
        self.career_data = {}
        self.salary_data = {}

    def get_nsw_act_universities(self):
        """Get list of NSW and ACT universities with basic info"""
        universities = {
            "University of Newcastle": {
                "location": "Newcastle, NSW",
                "website": "https://www.newcastle.edu.au",
                "type": "Public",
                "strengths": ["Engineering", "Medicine", "Education", "Business"]
            },
            "University of Sydney": {
                "location": "Sydney, NSW",
                "website": "https://www.sydney.edu.au",
                "type": "Public",
                "strengths": ["Law", "Medicine", "Arts", "Business", "Engineering"]
            },
            "University of New South Wales": {
                "location": "Sydney, NSW",
                "website": "https://www.unsw.edu.au",
                "type": "Public",
                "strengths": ["Engineering", "Business", "Medicine", "Law", "Arts"]
            },
            "Macquarie University": {
                "location": "Sydney, NSW",
                "website": "https://www.mq.edu.au",
                "type": "Public",
                "strengths": ["Ancient History", "Anthropology", "Education", "Languages", "Arts"],
                "special_features": ["Strong ancient history program", "Human sciences faculty",
                                     "Excellent teacher training"],
                "relevant_for": ["Rosa - Ancient History & Anthropology", "Reuben - Education & History"]
            },
            "University of Technology Sydney": {
                "location": "Sydney, NSW",
                "website": "https://www.uts.edu.au",
                "type": "Public",
                "strengths": ["Engineering", "IT", "Design", "Business"]
            },
            "Australian National University": {
                "location": "Canberra, ACT",
                "website": "https://www.anu.edu.au",
                "type": "Public",
                "strengths": ["Research", "Arts", "Science", "Policy", "Law"]
            },
            "University of Canberra": {
                "location": "Canberra, ACT",
                "website": "https://www.canberra.edu.au",
                "type": "Public",
                "strengths": ["Education", "Health", "Arts", "Business"]
            }
        }

        return universities

    def get_career_outlook_data(self):
        """Get Australian career outlook data"""
        career_data = {
            "Secondary School Teachers": {
                "employment_outlook": "Strong growth expected",
                "median_salary": "$85,000 - $95,000",
                "growth_rate": "8.5% (2023-2028)",
                "key_skills": ["Communication", "Subject expertise", "Classroom management"],
                "pathways": ["Bachelor of Education", "Bachelor + Master of Teaching"],
                "army_reserves_compatible": True
            },
            "Anthropologists": {
                "employment_outlook": "Moderate growth",
                "median_salary": "$75,000 - $90,000",
                "growth_rate": "4.2% (2023-2028)",
                "key_skills": ["Research", "Analysis", "Cultural understanding"],
                "pathways": ["Bachelor of Arts (Anthropology)", "Honours", "Masters"],
                "lab_work_involved": True
            },
            "Archaeologists": {
                "employment_outlook": "Stable demand",
                "median_salary": "$70,000 - $85,000",
                "growth_rate": "2.1% (2023-2028)",
                "key_skills": ["Fieldwork", "Laboratory analysis", "Documentation"],
                "pathways": ["Bachelor of Arts (Archaeology)", "Field experience"],
                "lab_work_involved": True
            },
            "Museum Curators": {
                "employment_outlook": "Limited but stable",
                "median_salary": "$65,000 - $80,000",
                "growth_rate": "1.8% (2023-2028)",
                "key_skills": ["Research", "Collection management", "Public education"],
                "pathways": ["Bachelor of Arts", "Museum Studies", "Postgraduate qualifications"],
                "lab_work_involved": False
            },
            "Writers and Authors": {
                "employment_outlook": "Growing demand",
                "median_salary": "$55,000 - $75,000",
                "growth_rate": "6.3% (2023-2028)",
                "key_skills": ["Writing", "Research", "Digital literacy"],
                "pathways": ["Bachelor of Arts (English/Creative Writing)", "Journalism"],
                "lab_work_involved": False
            }
        }
        return career_data

    def get_course_data_for_interests(self):
        """Get specific course data relevant to Rosa and Reuben's interests"""
        courses = {
            "Bachelor of Arts (Anthropology)": {
                "universities": ["University of Sydney", "ANU", "Macquarie University"],
                "duration": "3 years",
                "prerequisites": ["ATAR 80+", "English Advanced recommended"],
                "lab_components": ["Forensic anthropology labs", "Archaeological fieldwork",
                                   "Bioanthropology practicals"],
                "career_paths": ["Anthropologist", "Archaeologist", "Museum curator", "Cultural consultant"],
                "application_deadline": "September 30, 2025",
                "macquarie_specific": ["Human Sciences building with modern labs", "Field school opportunities",
                                       "Industry partnerships"]
            },
            "Bachelor of Education (Secondary)": {
                "universities": ["University of Newcastle", "University of Sydney", "UNSW"],
                "duration": "4 years",
                "prerequisites": ["ATAR 75+", "Literacy and numeracy tests"],
                "specializations": ["History", "English", "Languages", "Sciences"],
                "army_reserves_benefits": ["HECS support", "Leadership training", "Flexible study"],
                "application_deadline": "December 31, 2024"
            },
            "Bachelor of Arts (History)": {
                "universities": ["University of Sydney", "ANU", "Macquarie University"],
                "duration": "3 years",
                "prerequisites": ["ATAR 78+", "Strong English skills"],
                "specializations": ["Ancient history", "Modern history", "Asian studies"],
                "combined_degrees": ["Arts/Law", "Arts/Education"],
                "application_deadline": "January 15, 2025"
            },
            "Bachelor of Arts (Ancient History) - Macquarie": {
                "universities": ["Macquarie University"],
                "duration": "3 years",
                "prerequisites": ["ATAR 75+", "English Advanced or Extension"],
                "special_features": ["Museum Studies component", "Archaeological field work",
                                     "Hands-on artifact analysis"],
                "lab_components": ["Artifact conservation labs", "Archaeological analysis",
                                   "Digital archaeology tools"],
                "career_paths": ["Museum curator", "Archaeological consultant", "Heritage advisor",
                                 "Academic researcher"],
                "application_deadline": "January 15, 2025",
                "why_choose": "Perfect blend of Rosa's ancient history and practical lab interests"
            }
        }
        return courses

    def get_army_reserves_education_benefits(self):
        """Get Army Reserves education support information"""
        benefits = {
            "HECS-HELP Support": {
                "description": "Additional payments toward HECS debt",
                "amount": "Up to $27,000 over service period",
                "eligibility": "Active reserve service commitment"
            },
            "Undergraduate Scheme": {
                "description": "Support for undergraduate studies",
                "amount": "Up to $5,245 per year",
                "eligibility": "Enrolled in approved program"
            },
            "Leadership Training": {
                "description": "Military leadership qualifications",
                "benefits": "Transferable skills for teaching career",
                "time_commitment": "One weekend per month + annual camps"
            },
            "Flexible Study": {
                "description": "Study support and flexible service",
                "benefits": "Time off for exams and major assignments",
                "career_compatibility": "Excellent for teaching career"
            }
        }
        return benefits

    def collect_all_data(self):
        """Collect all data needed for the career explorer"""
        print("🔍 Collecting Australian education data...")

        self.university_data = self.get_nsw_act_universities()
        print("✅ University data collected")

        self.career_data = self.get_career_outlook_data()
        print("✅ Career outlook data collected")

        self.course_data = self.get_course_data_for_interests()
        print("✅ Course data collected")

        self.army_benefits = self.get_army_reserves_education_benefits()
        print("✅ Army Reserves benefits data collected")

        return {
            "universities": self.university_data,
            "careers": self.career_data,
            "courses": self.course_data,
            "army_benefits": self.army_benefits
        }

    def save_data_to_file(self, filename="education_data.json"):
        """Save collected data to JSON file"""
        all_data = self.collect_all_data()

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Data saved to {filename}")
        return filename


# Quick test function
def test_data_collection():
    collector = AustralianEducationDataCollector()
    data = collector.collect_all_data()

    print("\n📊 Sample Data Preview:")
    print(f"Universities: {len(data['universities'])}")
    print(f"Careers: {len(data['careers'])}")
    print(f"Courses: {len(data['courses'])}")
    print(f"Army Benefits: {len(data['army_benefits'])}")

    return data


if __name__ == "__main__":
    test_data_collection()