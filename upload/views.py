import pandas as pd
from django.shortcuts import render
from .forms import UploadFileForm
import os
from django.conf import settings
from django.core.mail import EmailMessage
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

def create_summary_image(data, filename):
    summary = data.describe(include='all')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')

    table = ax.table(cellText=summary.values, colLabels=summary.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)  
    
    media_dir = settings.MEDIA_ROOT
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    plt.savefig(os.path.join(media_dir, filename), bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    
def handle_uploaded_file(f):
    if f.name.endswith('.csv'):
        return pd.read_csv(f)
    elif f.name.endswith('.xlsx'):
        return pd.read_excel(f)
    else:
        return None

def summarize_data(data):
    # Generate a simple summary
    return {
        'columns': data.columns.tolist(),
        'summary': data.describe(),
        'head': data.head()
    }

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            if data is not None:
                
                summary = summarize_data(data)
                # Create summary image
                filename = 'summary.png'
                create_summary_image(data, filename)

                image_path = os.path.join(settings.MEDIA_ROOT, filename)
                
                email = EmailMessage(
                    subject='Python Assignment - AbidHussain',
                    body=f'Please find the summary report attached.\n\nSummary:\n{summary}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['falconenemy50@gmail.com'],
                )

                email.attach_file(image_path)

               
                email.send(fail_silently=False)
                return render(request, 'success.html', {'summary_image': filename, 'summary': summary})
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

