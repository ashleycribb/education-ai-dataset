# lms_frontend_flask/data_models.py

COURSES = {
    "course1": {
        "id": "course1",
        "title": "4th Grade Reading Comprehension",
        "description": "Develop reading comprehension skills for 4th graders, focusing on main ideas, details, and vocabulary.",
    },
    "course2": {
        "id": "course2",
        "title": "Introduction to Fractions (4th Grade)",
        "description": "Learn the basics of fractions, including understanding parts of a whole and equivalent fractions.",
    },
}

MODULES = {
    "module1_c1": {
        "id": "module1_c1",
        "title": "Understanding Stories",
        "course_id": "course1",
        "description": "Focus on key elements of story comprehension.",
    },
    "module2_c1": {
        "id": "module2_c1",
        "title": "Vocabulary Building",
        "course_id": "course1",
        "description": "Learn new words and how to understand them in context.",
    },
    "module1_c2": {
        "id": "module1_c2",
        "title": "What is a Fraction?",
        "course_id": "course2",
        "description": "Introduction to the concept of fractions.",
    },
}

ACTIVITIES = {
    "activity_lost_kite_m1c1": {
        "id": "activity_lost_kite_m1c1",
        "title": "Reading: The Lost Kite",
        "module_id": "module1_c1",
        "description": "Read the story 'The Lost Kite' and prepare to discuss its main idea.",
        "ai_activity_key": "lost_kite_activity", # Matches a key in AIAssistant's get_current_activity
        "content_type": "reading_passage",
        "content": "Once upon a time, in a park full of tall green trees and colorful flowers, a little boy named Tom was flying his bright red kite. The kite danced in the wind, soaring high above the tallest oak. Tom laughed, holding onto the string tightly. Suddenly, a strong gust of wind tugged hard. Snap! The string broke, and the kite flew away, disappearing over the trees. Tom felt a pang of sadness; his favorite kite was gone. He searched and searched, his heart growing heavier with each step. Just as he was about to give up, he saw a flash of red tangled in the branches of a distant tree. With the help of a friendly park ranger and a long ladder, Tom rescued his kite. He was overjoyed and thanked the ranger with a big smile."
    },
    "activity_main_idea_m1c1": {
        "id": "activity_main_idea_m1c1",
        "title": "Activity: Main Idea of 'The Lost Kite'",
        "module_id": "module1_c1",
        "description": "Identify and discuss the main idea of 'The Lost Kite' with the AI assistant.",
        "ai_activity_key": "lost_kite_activity", # This key should map to an activity in the AI assistant
        "content_type": "ai_interaction",
        "content": "Let's work with the AI assistant to find the main idea of the story.",
    },
    "activity_vocab_anxious_m2c1": {
        "id": "activity_vocab_anxious_m2c1",
        "title": "Vocabulary: 'Anxious'",
        "module_id": "module2_c1",
        "description": "Learn the meaning of the word 'anxious' with the AI assistant.",
        "ai_activity_key": "lost_kite_activity", # This key should map to an activity in the AI assistant
        "content_type": "ai_interaction",
        "content": "Let's explore the word 'anxious' with our AI assistant.",
    },
    "activity_what_is_fraction_m1c2": {
        "id": "activity_what_is_fraction_m1c2",
        "title": "Understanding Halves and Quarters",
        "module_id": "module1_c2",
        "description": "An interactive lesson on understanding 1/2 and 1/4.",
        "ai_activity_key": "fractions_activity", # This key should map to an activity in the AI assistant
        "content_type": "ai_interaction",
        "content": "Join the AI assistant to learn about halves and quarters!",
    },
}

# Helper functions to get related items
def get_modules_for_course(course_id):
    return [module for module in MODULES.values() if module['course_id'] == course_id]

def get_activities_for_module(module_id):
    return [activity for activity in ACTIVITIES.values() if activity['module_id'] == module_id]
