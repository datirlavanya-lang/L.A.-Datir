from django.shortcuts import render,redirect
from .models import Note

# Create your views here.
def note_list(request):
    notes=Note.objects.all().order_by('-created_at')
    return render(request,'notes/note_list.html',{'notes':notes})

def add_note(request):
    if request.method=='POST':
        title=request.POST.get('title')
        content=request.POST.get('content')

        Note.objects.create(title=title,content=content)
        return redirect('note_list')
    return render(request,'notes/add_note.html')
    
    