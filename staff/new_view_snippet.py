@staff_required
def add_marks(request, exam_id):
    exam = get_object_or_404(ExamRegistration, id=exam_id)
    students = StudentReg.objects.filter(
        course=exam.course, sem=exam.sem, login_info__status="V"
    ).order_by("reg_no")

    if request.method == "POST":
        for student in students:
            mark_value = request.POST.get(f"mark_{student.id}")
            if mark_value:
                # Update or create mark entry
                MarkList.objects.update_or_create(
                    exam=exam, student=student, defaults={"marks": mark_value}
                )
        messages.success(request, "Marks added successfully")
        return redirect("staff_home")

    # Pre-fetch existing marks if any
    existing_marks = MarkList.objects.filter(exam=exam)
    marks_map = {m.student_id: m.marks for m in existing_marks}

    student_data = []
    for s in students:
        student_data.append({"student": s, "mark": marks_map.get(s.id, "")})

    return render(
        request, "staff/add_marks.html", {"exam": exam, "student_data": student_data}
    )
