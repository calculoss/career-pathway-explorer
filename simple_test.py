# Quick test to verify your Canvas integration is working
# Run this in your Python environment to test:

def test_canvas_integration():
    """Test script to verify Canvas integration is working"""

    print("🧪 Testing Canvas Integration...")

    # Test 1: Import Canvas integration
    try:
        from canvas_integration import CanvasIntegrator, SimpleMilestoneGenerator
        print("✅ Canvas integration imports working")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Test 2: Initialize Canvas integrator
    try:
        canvas_integrator = CanvasIntegrator()
        print("✅ Canvas integrator initializes successfully")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

    # Test 3: Initialize database
    try:
        from multi_family_database import MultiFamilyDatabase
        db = MultiFamilyDatabase()
        print("✅ Database with Canvas tables initializes successfully")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

    # Test 4: Test milestone generator
    try:
        milestone_gen = SimpleMilestoneGenerator()
        print("✅ Milestone generator initializes successfully")
    except Exception as e:
        print(f"❌ Milestone generator error: {e}")
        return False

    print("🎉 All Canvas integration tests passed!")
    return True


if __name__ == "__main__":
    test_canvas_integration()