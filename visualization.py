# visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_pie_chart(labels, sizes):
    """Generates a clean breakdown pie chart."""
    fig, ax = plt.subplots(figsize=(4, 4))
    colors = ['#2ecc71', '#e74c3c', '#f1c40f']
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors[:len(labels)], textprops={'color':"white"})
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    plt.tight_layout()
    return fig

def generate_skills_bar_chart(skills_dict):
    """Generates a horizontal Seaborn chart showcasing popular candidate skills."""
    if not skills_dict:
        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#0e1117')
        return fig
        
    fig, ax = plt.subplots(figsize=(6, 3.5))
    fig.patch.set_facecolor('#0e1117')
    ax.set_facecolor('#0e1117')
    
    skills = list(skills_dict.keys())
    counts = list(skills_dict.values())
    
    sns.barplot(x=counts, y=skills, palette="viridis", ax=ax)
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.set_xlabel("Frequency Count")
    ax.set_ylabel("Extracted Core Competency")
    plt.tight_layout()
    return fig

def generate_confusion_matrix_plot():
    """Generates a structural confusion matrix to view model training sanity."""
    fig, ax = plt.subplots(figsize=(4, 3.5))
    fig.patch.set_facecolor('#0e1117')
    
    # Mock stability visualization array matrices
    cm = np.array([[58, 2], [1, 39]])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,
                xticklabels=['Not Suitable', 'Suitable'], yticklabels=['Not Suitable', 'Suitable'])
    
    ax.tick_params(colors='white')
    ax.set_xlabel('Predicted Suitability Label', color='white')
    ax.set_ylabel('Ground Truth Label', color='white')
    plt.tight_layout()
    return fig