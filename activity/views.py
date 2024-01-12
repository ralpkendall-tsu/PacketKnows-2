from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from .models import Activity
from classroom.models import Enrollment, Classroom 
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce

# Create your views here.
def ActivityView(request):
    if request.method == 'POST':
        # Handle POST requests if needed
        pass
    else:
        class_id = request.GET.get('class_id')

        # Ensure class_id is not None and is a valid integer
        if class_id is not None and class_id.isdigit():
            class_id = int(class_id)
            
            # Use get_object_or_404 to handle cases where the enrollment is not found
            enrollment = get_object_or_404(Enrollment, student=request.user, classroom__id=class_id)
            
            # Retrieve activities for the enrollment
            activities = enrollment.activities.all()

            # Generate HTML string with <li> tags
            li_tags = ''.join([f'<li data-activity-id="{ activity.id }">{activity.base_activity.number}</li>' for activity in activities])

            # Return an HttpResponse with the generated HTML
            return HttpResponse(li_tags)
        else:
            # Handle the case where class_id is not provided or not a valid integer
            return HttpResponse('Invalid or missing class_id', status=400)
        
def ActivityOptions(request):
    context={}
    if request.method == 'POST':
        # Handle POST requests if needed
        pass
    else:
        
        classroom_id = request.GET.get('classroomID', None)
        enrollment = Enrollment.objects.get(student=request.user, classroom_id=classroom_id)
        activities = enrollment.activities.all()
        
        context["activities"] = activities
        
        return render(request, 'core/help/student-help-activity-partial.html', context)
    
def serve_pdf(request, pdf_path):
    # Assuming pdf_path is the path to your PDF file in the media directory
    pdf_path = pdf_path.lstrip('/')
    pdf_file = open(pdf_path, 'rb')
    response = FileResponse(pdf_file)
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'inline; filename="your_file.pdf"'
    response['X-Frame-Options'] = 'ALLOWALL'
    return response
    
    
    
def compute_student_rank(student, classroom):
    enrollments = Enrollment.objects.filter(classroom=classroom)
    studentFinalGrades = []
    for enrollment in enrollments:
        student = enrollment.student
        trainingReport = computeTrainingProgressReport(student=student,classroom=classroom)
        testingReport = computeTestingProgressReport(student=student,classroom=classroom)
        studentFinalGrade = round((trainingReport["total_training_percentage"] + testingReport["total_testing_percentage"]) / 2, 2)
        studentGrade = {
            "id": student.id,
            "finalGrade": studentFinalGrade
        }
        studentFinalGrades.append(studentGrade)
        
    sorted_student_final_grades = sorted(studentFinalGrades, key=lambda x: x['finalGrade'], reverse=True)
    user_rank = next((index + 1 for index, student_grade in enumerate(sorted_student_final_grades) if student_grade['id'] == student.id), None)

    
    return user_rank

def computeClassRanks(classroom):
    # Only for TESTING MODE
    enrollments = Enrollment.objects.filter(classroom=classroom)
    studentFinalGrades = []
    for enrollment in enrollments:
        student = enrollment.student
        testingReport = computeTestingProgressReport(student=student,classroom=classroom)
        studentFinalGrade = round(testingReport["total_testing_percentage"], 2)
        studentGrade = {
            "id": student.id,
            "name": student.first_name + " " + student.last_name,
            "finalGrade": studentFinalGrade
        }
        studentFinalGrades.append(studentGrade)
        
    sorted_student_final_grades = sorted(studentFinalGrades, key=lambda x: x['finalGrade'], reverse=True)

    
    return sorted_student_final_grades
        
    
    
        
def computeSingleActivityScore(student, activity_id):
    try:
        result = {
            'labels': [],
            'data': [],
        }

        # Assuming activity_id is unique per activity
        activity = Activity.objects.get(id=activity_id)

        # Assuming the activity has a related base_activity
        base_activity = activity.base_activity

        # Assuming you want to calculate the scores for the 5 categories
        category_percentages = {
            'physical_percentage': round((activity.physical_points / base_activity.max_physical_points) * 100, 2),
            'basic_config_percentage': round((activity.basic_config_points / base_activity.max_basic_config_points) * 100, 2),
            'ip_percentage': round((activity.ip_points / base_activity.max_ip_points) * 100, 2),
            'routing_percentage': round((activity.routing_points / base_activity.max_routing_points) * 100, 2),
            'other_percentage': round((activity.other_points / base_activity.max_other_points) * 100, 2),
        }

        # Populate the labels and data for the bar chart
        for category, percentage in category_percentages.items():
            result['labels'].append(category.replace('_percentage', '').capitalize())
            result['data'].append(percentage)

        return result

    except Activity.DoesNotExist:
        return None
        
def update_chart_data(request, mode):
    average_progress = computeAverageClassProgress(request.user, mode)

    data = average_progress['averages']
    labels = average_progress['class_names']
    
    average = round(sum(data) / len(data), 2)

    return JsonResponse({'chartData': data, 'chartLabels': labels, 'average':average})
        

def computeAverageClassProgress(student, mode):
    result = {
        'class_names': [],
        'averages': [],
    }

    try:
        enrollments = Enrollment.objects.filter(student=student)
        for enrollment in enrollments:
            activities = enrollment.activities.filter(mode=mode)

            if activities.exists():
                class_average = sum(calculatePercentage(activity)['total_percentage'] for activity in activities) / len(activities)
                result['class_names'].append(enrollment.classroom.name)
                result['averages'].append(round(class_average, 2))

    except Enrollment.DoesNotExist:
        return None

    return result

def computeClassStrengthRating(student, classroom):
    try:
        all_activities = []

        enrollments = Enrollment.objects.filter(student=student, classroom=classroom)
        for enrollment in enrollments:
            all_activities.extend(enrollment.activities.all())
        all_percentages = [calculatePercentage(activity) for activity in all_activities]
        top_categories = computeTopCategories(all_percentages)

        return top_categories

    except Enrollment.DoesNotExist:
        return None
    
def computeOverallStrengthRating(student):
    try:
        all_activities = []

        enrollments = Enrollment.objects.filter(student=student)
        for enrollment in enrollments:
            all_activities.extend(enrollment.activities.all())
        all_percentages = [calculatePercentage(activity) for activity in all_activities]
        top_categories = computeTopCategories(all_percentages)

        return top_categories

    except Enrollment.DoesNotExist:
        return None
        
def computeTopCategories(activities):
    category_percentages = {}

    for activity in activities:
        for key in ['physical_percentage', 'basic_config_percentage', 'ip_percentage', 'routing_percentage', 'other_percentage']:
            if key not in category_percentages:
                category_percentages[key] = []

            category_percentages[key].append(activity[key])

    average_percentages = {}

    for key, values in category_percentages.items():
        average_percentage = sum(values) / len(values) if values else None
        average_percentages[key] = average_percentage

    # Sort the categories based on average_percentage in descending order
    sorted_categories = sorted(average_percentages.items(), key=lambda x: x[1], reverse=True)


    result = []

    for category in sorted_categories:
        result.append({
            'name': category[0].replace('_percentage', '').capitalize(),
            'average_percentage': round(category[1], 2) if category[1] is not None else None
        })

    return result

def computeTrainingProgressReport(student, classroom):
    result = {
        'training_percentages': None,
        'total_training_percentage': None,
        'top_training_categories': None,
    }

    try:
        enrollment = Enrollment.objects.get(student=student, classroom=classroom)
        training_activities = enrollment.activities.filter(mode="training")

        training_percentages = [calculatePercentage(activity) for activity in training_activities]

        total_training_percentage = (
            sum(percentage['total_percentage'] for percentage in training_percentages) /
            len(training_percentages)
        ) if training_percentages else None

        top_training_categories = computeTopCategories(training_percentages)

        result['training_percentages'] = training_percentages
        result['total_training_percentage'] = total_training_percentage
        result['top_training_categories'] = top_training_categories

    except Enrollment.DoesNotExist:
        return None

    return result

def computeTestingProgressReport(student, classroom):
    result = {
        'testing_percentages': None,
        'total_testing_percentage': None,
        'top_testing_categories': None,
    }

    try:
        enrollment = Enrollment.objects.get(student=student, classroom=classroom)
        testing_activities = enrollment.activities.filter(mode="testing")

        testing_percentages = [calculatePercentage(activity) for activity in testing_activities]

        total_testing_percentage = (
            sum(percentage['total_percentage'] for percentage in testing_percentages) /
            len(testing_percentages)
        ) if testing_percentages else None

        top_testing_categories = computeTopCategories(testing_percentages)

        result['testing_percentages'] = testing_percentages
        result['total_testing_percentage'] = total_testing_percentage
        result['top_testing_categories'] = top_testing_categories

    except Enrollment.DoesNotExist:
        return None

    return result


def calculatePercentage(activity):
    try:
        base_activity = activity.base_activity

        physical_percentage = round((activity.physical_points / base_activity.max_physical_points) * 100, 2)
        basic_config_percentage = round((activity.basic_config_points / base_activity.max_basic_config_points) * 100, 2)
        ip_percentage = round((activity.ip_points / base_activity.max_ip_points) * 100, 2)
        routing_percentage = round((activity.routing_points / base_activity.max_routing_points) * 100, 2)
        other_percentage = round((activity.other_points / base_activity.max_other_points) * 100, 2)

        total_percentage = round(
            sum([physical_percentage, basic_config_percentage, ip_percentage, routing_percentage, other_percentage]) / 5,
            2
        )

        return {
            'number': base_activity.number,
            'name': base_activity.name,
            'physical_percentage': physical_percentage,
            'basic_config_percentage': basic_config_percentage,
            'ip_percentage': ip_percentage,
            'routing_percentage': routing_percentage,
            'other_percentage': other_percentage,
            'total_percentage': total_percentage
        }
    except:
        return None
