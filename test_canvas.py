from canvas_sync_module import CanvasSyncManager, CanvasAPIClient, CanvasDataSync


# Test the Canvas connection
def test_with_rosa_reuben():
    print("🧪 Testing Canvas Integration...")

    # Initialize
    sync_manager = CanvasSyncManager()

    # Test connection (replace with real details)
    canvas_url = "https://lambtonhs.instructure.com/"
    access_token = "20803~2FYXEnvmrfw3m42UWhw28enfLTkwT3HuNM9mYHJ4K8KRCEZTty8cQ9GRrH3R3AZL"

    client = CanvasAPIClient(canvas_url, access_token)
    result = client.test_connection()

    print(f"Connection result: {result}")

    if result['status'] == 'success':
        # Get courses and assignments
        courses = client.get_courses()
        print(f"Found {len(courses)} courses")

        assignments = client.get_upcoming_assignments_all_courses()
        print(f"Found {len(assignments)} upcoming assignments")

        for assignment in assignments[:5]:  # Show first 5
            print(f"- {assignment.name} ({assignment.course_name}) - Due: {assignment.due_date}")


if __name__ == "__main__":
    test_with_rosa_reuben()