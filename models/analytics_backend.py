import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import random

def plot_employee_statuses(save_path):
    labels = ["Working", "Paid_Leave", "AWOL", "Day_off"]
    sizes = [random.randint(5, 20) for _ in labels]
    colors = ['#03335e', '#1579c0', '#b2dbf8', '#598cb8']

    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    plt.title('Employee Statuses')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_vehicles_deployed(save_path):
    deployed = random.randint(5, 15)
    total = deployed + random.randint(2, 10)
    plt.figure(figsize=(5, 4))
    plt.bar(['Deployed', 'Available'], [deployed, total - deployed], color=['#1579c0', '#b2dbf8'])
    plt.title('Vehicles Deployment')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()