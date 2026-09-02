from flask import Flask, render_template, url_for, abort
from .config import Config
from .extensions import db
from .models import Course, Module, Activity

# Flask-Admin imports
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Flask-Admin setup
admin = Admin(app, name='LMS Content Admin', template_mode='bootstrap3')
# Add administrative views here
# Define custom ModelViews if needed for more control
class SecureModelView(ModelView):
    # pass # Add authentication and authorization logic here later
    # For now, it's open
    def is_accessible(self):
        # Placeholder for admin access control
        return True

admin.add_view(SecureModelView(Course, db.session))
admin.add_view(SecureModelView(Module, db.session))
admin.add_view(SecureModelView(Activity, db.session))

def get_nav_items():
    """Helper function to provide navigation items for templates."""
    courses = Course.query.order_by(Course.title).all()
    navigation_items = []
    for course in courses:
        # Accessing course.modules will execute the query due to lazy='dynamic'
        # For navigation, we might not need all module details, just title and ext_id
        # But for simplicity, fetching them all for now.
        modules_data = [{"id": mod.id, "module_ext_id": mod.module_ext_id, "title": mod.title} for mod in course.modules.order_by(Module.title).all()]
        course_item = {
            "id": course.id, # Using internal DB id for nav item structure
            "course_ext_id": course.course_ext_id,
            "title": course.title,
            "modules": modules_data
        }
        navigation_items.append(course_item)
    return navigation_items

@app.context_processor
def inject_navigation():
    """Injects navigation_items into the context of all templates."""
    return dict(navigation_items=get_nav_items(), get_activities_for_module=get_activities_for_module_helper)

def get_activities_for_module_helper(module_id_internal):
    """Helper to get activities for a module by its internal ID, for use in templates if needed"""
    # This is a simplified version. In templates, it's better to pass activities directly from the route.
    # This specific helper might not be directly used by activity_page.html's nav block if nav items are already complete.
    module = Module.query.get(module_id_internal)
    if module:
        return [{"id": act.id, "activity_ext_id": act.activity_ext_id, "title": act.title} for act in module.activities.order_by(Activity.title).all()]
    return []


@app.route('/')
def home():
    # navigation_items are injected by context_processor
    return render_template('index.html')

@app.route('/course/<string:course_ext_id>/module/<string:module_ext_id>')
def show_module_activities(course_ext_id, module_ext_id):
    course = Course.query.filter_by(course_ext_id=course_ext_id).first_or_404()
    module = Module.query.filter_by(module_ext_id=module_ext_id, course_id=course.id).first_or_404()
    activities = module.activities.order_by(Activity.title).all()
    # navigation_items are injected by context_processor
    return render_template('module_page.html', course=course, module=module, activities=activities)

@app.route('/course/<string:course_ext_id>/module/<string:module_ext_id>/activity/<string:activity_ext_id>')
def show_activity(course_ext_id, module_ext_id, activity_ext_id):
    course = Course.query.filter_by(course_ext_id=course_ext_id).first_or_404()
    module = Module.query.filter_by(module_ext_id=module_ext_id, course_id=course.id).first_or_404()
    activity = Activity.query.filter_by(activity_ext_id=activity_ext_id, module_id=module.id).first_or_404()
    # navigation_items are injected by context_processor
    return render_template('activity_page.html', course=course, module=module, activity=activity)

# Dummy API routes for url_for in templates (to be implemented later)
@app.route('/api/activity/start', methods=['POST'])
def start_ai_activity_api():
    return {"status": "AI activity started (dummy response)", "session_id": "dummy_session_123"}

@app.route('/api/activity/interact', methods=['POST'])
def interact_ai_activity_api():
    return {"ai_messages": ["AI response (dummy)"], "xapi_statements": [], "is_activity_complete": False}

def create_tables():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created (if they didn't exist).")
        # Optional: Seed initial data here if needed for development
        seed_data()


def seed_data():
    with app.app_context():
        if Course.query.first() is None: # Check if data already exists
            print("Seeding initial data...")
            # Create Roles (if you had a Role model and user roles for admin)

            # Create Courses
            course1 = Course(course_ext_id="reading_comp_g4", title="4th Grade Reading Comprehension", description="Develop reading comprehension skills for 4th graders.")
            course2 = Course(course_ext_id="fractions_g4", title="Introduction to Fractions (4th Grade)", description="Learn the basics of fractions.")
            db.session.add_all([course1, course2])
            db.session.commit() # Commit courses to get their IDs

            # Create Modules
            module1_c1 = Module(module_ext_id="stories_m1c1", title="Understanding Stories", course_id=course1.id, description="Focus on key elements of story comprehension.")
            module2_c1 = Module(module_ext_id="vocab_m2c1", title="Vocabulary Building", course_id=course1.id, description="Learn new words in context.")
            module1_c2 = Module(module_ext_id="intro_frac_m1c2", title="What is a Fraction?", course_id=course2.id, description="Introduction to the concept of fractions.")
            db.session.add_all([module1_c1, module2_c1, module1_c2])
            db.session.commit() # Commit modules to get their IDs

            # Create Activities
            act1_m1c1 = Activity(activity_ext_id="lost_kite_read_a1m1c1", title="Reading: The Lost Kite", module_id=module1_c1.id,
                                 description="Read the story 'The Lost Kite'.", ai_activity_key="lost_kite_activity",
                                 content_type="reading_passage", content="Once upon a time, in a park...")
            act2_m1c1 = Activity(activity_ext_id="lost_kite_main_idea_a2m1c1", title="Activity: Main Idea of 'The Lost Kite'", module_id=module1_c1.id,
                                 description="Identify the main idea with the AI assistant.", ai_activity_key="lost_kite_activity",
                                 content_type="ai_interaction", content="Let's find the main idea.")
            act1_m2c1 = Activity(activity_ext_id="vocab_anxious_a1m2c1", title="Vocabulary: 'Anxious'", module_id=module2_c1.id,
                                 description="Learn 'anxious' with the AI assistant.", ai_activity_key="lost_kite_activity", # Assuming same AI activity for this example
                                 content_type="ai_interaction", content="Let's explore 'anxious'.")
            act1_m1c2 = Activity(activity_ext_id="halves_quarters_a1m1c2", title="Understanding Halves and Quarters", module_id=module1_c2.id,
                                 description="Interactive lesson on 1/2 and 1/4.", ai_activity_key="fractions_activity",
                                 content_type="ai_interaction", content="Join the AI to learn about halves and quarters!")
            db.session.add_all([act1_m1c1, act2_m1c1, act1_m2c1, act1_m1c2])
            db.session.commit()
            print("Initial data seeded.")
        else:
            print("Data already exists, skipping seed.")


if __name__ == '__main__':
    create_tables() # Create tables and seed data if running directly
    app.run(debug=True, port=5000)
