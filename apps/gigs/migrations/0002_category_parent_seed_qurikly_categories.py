from django.db import migrations, models
import django.db.models.deletion


QURIKLY_CATEGORIES = {
    "Web Development": [
        "Frontend Development",
        "Backend Development",
        "Full Stack Development",
        "WordPress Development",
        "Django Development",
        "React Development",
    ],
    "App Development": [
        "Android Apps",
        "iOS Apps",
        "Flutter Development",
        "React Native",
    ],
    "UI/UX & Design": [
        "UI Design",
        "UX Design",
        "Figma Design",
        "Logo Design",
        "Poster Design",
        "Thumbnail Design",
    ],
    "AI & Machine Learning": [
        "Machine Learning Models",
        "Chatbot Development",
        "AI Automation",
        "NLP Projects",
        "Computer Vision",
    ],
    "Data Science & Analytics": [
        "Data Analysis",
        "Data Visualization",
        "Power BI Dashboards",
        "Tableau Dashboards",
        "Excel Analytics",
    ],
    "Content Writing": [
        "Blog Writing",
        "Technical Writing",
        "Copywriting",
        "Resume Writing",
        "Product Descriptions",
    ],
    "Video & Animation": [
        "Video Editing",
        "Motion Graphics",
        "Reels Editing",
        "YouTube Editing",
        "Animation",
    ],
    "Digital Marketing": [
        "SEO",
        "Social Media Marketing",
        "Email Marketing",
        "Ads Management",
        "Content Marketing",
    ],
    "Programming & Tech": [
        "Java Projects",
        "Python Projects",
        "C++ Coding",
        "API Integration",
        "Bug Fixing",
    ],
    "Cybersecurity": [
        "Security Testing",
        "Vulnerability Assessment",
        "Network Security",
        "Ethical Hacking Basics",
    ],
    "Cloud & DevOps": [
        "Docker Setup",
        "AWS Services",
        "CI/CD Pipelines",
        "Jenkins Setup",
        "Kubernetes",
    ],
    "Academic & Student Help": [
        "PPT Creation",
        "Assignment Help",
        "Project Documentation",
        "Research Assistance",
    ],
    "Student Freelancers": [
        "College Students",
        "Beginners",
        "Affordable Services",
    ],
    "Startup Support": [
        "MVP Development",
        "Landing Pages",
        "Pitch Deck Design",
        "Business Websites",
    ],
    "Quick Tasks": [
        "Fix Bugs",
        "Edit Resumes",
        "Make Posters",
        "Deploy Websites",
    ],
}


def get_or_create_category(Category, name, parent=None):
    category = Category.objects.filter(name=name, parent=parent).first()
    if category:
        return category

    if parent is not None:
        category = Category.objects.filter(name=name, parent__isnull=True).first()
        if category:
            category.parent = parent
            category.save(update_fields=["parent"])
            return category

    return Category.objects.create(name=name, parent=parent)


def seed_qurikly_categories(apps, schema_editor):
    Category = apps.get_model("gigs", "Category")

    for main_name, subcategory_names in QURIKLY_CATEGORIES.items():
        main_category = get_or_create_category(Category, main_name)
        for subcategory_name in subcategory_names:
            get_or_create_category(Category, subcategory_name, main_category)


class Migration(migrations.Migration):

    dependencies = [
        ("gigs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subcategories",
                to="gigs.category",
            ),
        ),
        migrations.AlterModelOptions(
            name="category",
            options={
                "ordering": ["parent__name", "name"],
                "verbose_name_plural": "Categories",
            },
        ),
        migrations.RunPython(seed_qurikly_categories, migrations.RunPython.noop),
    ]
