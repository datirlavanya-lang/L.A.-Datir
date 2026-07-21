from django.shortcuts import render

def quiz_view(request):
    questions = [
        {
            'question': 'What is the capital of India?',
            'options': ['Mumbai', 'New Delhi', 'Kolkata', 'Chennai'],
            'answer': 'New Delhi'
        },
        {
            'question': 'Which planet is known as the Red Planet?',
            'options': ['Earth', 'Mars', 'Jupiter', 'Venus'],
            'answer': 'Mars'
        },
        {
            'question': 'Which country has the most olympic medals?',
            'options':['USA','Germany','China','UK'],
            'answer':'USA'
        },
        {
            'question':"Which one of the following is the world's oldest civilization?",
            'options':['China','Egypt','India','Japan'],
            'answer':'Egypt'
        },
        {
            'question':'Which continent has the most countries?',
            'options':['Asia','Africa','Europe','South America'],
            'answer':'Africa'
        },
        {
            'Thank you for participating!',
            'The quiz has now ended!'
        }
    ]

    q_index = int(request.GET.get('q', 0))
    question = questions[q_index]

    if request.method == 'POST':
        selected = request.POST.get('option')

        return render(request, 'QuizApp/quizquestions.html', {
            'question': question['question'],
            'options': question['options'],
            'selected': selected,
            'correct': question['answer'],
            'next_q': q_index + 1
        })

    return render(request, 'QuizApp/quizquestions.html', {
        'question': question['question'],
        'options': question['options'],
        'q_index': q_index
    })


