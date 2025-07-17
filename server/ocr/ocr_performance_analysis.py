#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
from collections import defaultdict
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# English font settings for PNG output
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def extract_performance_data(file_path):
    """Extract performance time data from OCR test result file."""
    
    paddleocr_times = []
    easyocr_times = []
    llm_times = []
    total_times = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by test case separator
    test_cases = content.split('=' * 60)
    
    for case in test_cases:
        if not case.strip():
            continue
            
        # Extract PaddleOCR execution time
        paddle_match = re.search(r'PaddleOCR 수행 시간: ([\d.]+)초', case)
        if paddle_match:
            paddleocr_times.append(float(paddle_match.group(1)))
        
        # Extract EasyOCR execution time
        easy_match = re.search(r'EasyOCR 수행 시간: ([\d.]+)초', case)
        if easy_match:
            easyocr_times.append(float(easy_match.group(1)))
        
        # Extract LLM execution time
        llm_match = re.search(r'LLM 수행 시간: ([\d.]+)초', case)
        if llm_match:
            llm_times.append(float(llm_match.group(1)))
        
        # Calculate total only when all three times are available
        if paddle_match and easy_match and llm_match:
            total_time = float(paddle_match.group(1)) + float(easy_match.group(1)) + float(llm_match.group(1))
            total_times.append(total_time)
    
    return {
        'paddleocr': paddleocr_times,
        'easyocr': easyocr_times,
        'llm': llm_times,
        'total': total_times
    }

def create_performance_visualizations(data):
    """Create visualizations for performance time data."""
    
    # 1. Individual model performance distribution (boxplot)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('OCR and LLM Performance Analysis', fontsize=16, fontweight='bold')
    
    # 1-1. Individual model boxplot
    ax1 = axes[0, 0]
    models = ['PaddleOCR', 'EasyOCR', 'LLM']
    times_data = [data['paddleocr'], data['easyocr'], data['llm']]
    
    bp = ax1.boxplot(times_data, labels=models, patch_artist=True)
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax1.set_title('Individual Model Performance Distribution')
    ax1.set_ylabel('Execution Time (seconds)')
    ax1.grid(True, alpha=0.3)
    
    # 1-2. Average performance comparison (bar chart)
    ax2 = axes[0, 1]
    avg_times = [np.mean(data['paddleocr']), np.mean(data['easyocr']), np.mean(data['llm'])]
    total_avg = np.mean(data['total'])
    models_bar = ['PaddleOCR', 'EasyOCR', 'LLM', 'Total']
    avg_times_bar = avg_times + [total_avg]
    colors_bar = colors + ['mediumpurple']
    bars = ax2.bar(models_bar, avg_times_bar, color=colors_bar, alpha=0.7)

    # Display average values on bars
    for bar, avg in zip(bars, avg_times_bar):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{avg:.2f}s', ha='center', va='bottom', fontweight='bold')

    ax2.set_title('Average Performance Comparison')
    ax2.set_ylabel('Average Execution Time (seconds)')
    ax2.grid(True, alpha=0.3)
    
    # 1-3. Total execution time distribution
    ax3 = axes[1, 0]
    ax3.hist(data['total'], bins=15, color='skyblue', alpha=0.7, edgecolor='black')
    ax3.axvline(np.mean(data['total']), color='red', linestyle='--', 
                label=f'Mean: {np.mean(data["total"]):.2f}s')
    ax3.set_title('Total Execution Time Distribution')
    ax3.set_xlabel('Total Execution Time (seconds)')
    ax3.set_ylabel('Frequency')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 1-4. Model time ratio (pie chart)
    ax4 = axes[1, 1]
    total_avg = np.mean(data['total'])
    percentages = [np.mean(data['paddleocr'])/total_avg*100, 
                   np.mean(data['easyocr'])/total_avg*100,
                   np.mean(data['llm'])/total_avg*100]
    
    wedges, texts, autotexts = ax4.pie(percentages, labels=models, autopct='%1.1f%%',
                                       colors=colors, startangle=90)
    ax4.set_title('Model Time Ratio')
    
    plt.tight_layout()
    plt.savefig('ocr_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return {
        'models': models,
        'times_data': times_data,
        'avg_times': avg_times,
        'percentages': percentages
    }

def create_time_series_plot(data):
    """Create time series visualization for execution time changes with outlier filtering."""
    
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle('Execution Time Changes by Test Case (Outliers Filtered)', fontsize=16, fontweight='bold')
    
    # Function to filter outliers using IQR method
    def filter_outliers(times, factor=1.5):
        """Filter outliers using Interquartile Range (IQR) method."""
        q1 = np.percentile(times, 25)
        q3 = np.percentile(times, 75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        
        # Create mask for non-outlier values
        mask = (times >= lower_bound) & (times <= upper_bound)
        return mask, lower_bound, upper_bound
    
    # Filter outliers for each model
    paddle_mask, paddle_lower, paddle_upper = filter_outliers(data['paddleocr'])
    easy_mask, easy_lower, easy_upper = filter_outliers(data['easyocr'])
    llm_mask, llm_lower, llm_upper = filter_outliers(data['llm'])
    total_mask, total_lower, total_upper = filter_outliers(data['total'])
    
    # Individual model time changes
    ax1 = axes[0]
    x = range(len(data['paddleocr']))
    
    # Plot filtered data
    ax1.plot(np.array(x)[paddle_mask], np.array(data['paddleocr'])[paddle_mask], 
             'o-', label='PaddleOCR', color='blue', alpha=0.7)
    ax1.plot(np.array(x)[easy_mask], np.array(data['easyocr'])[easy_mask], 
             's-', label='EasyOCR', color='green', alpha=0.7)
    ax1.plot(np.array(x)[llm_mask], np.array(data['llm'])[llm_mask], 
             '^-', label='LLM', color='red', alpha=0.7)
    
    # Add outlier points as small dots
    ax1.plot(np.array(x)[~paddle_mask], np.array(data['paddleocr'])[~paddle_mask], 
             'o', color='blue', alpha=0.3, markersize=3, label='PaddleOCR Outliers')
    ax1.plot(np.array(x)[~easy_mask], np.array(data['easyocr'])[~easy_mask], 
             's', color='green', alpha=0.3, markersize=3, label='EasyOCR Outliers')
    ax1.plot(np.array(x)[~llm_mask], np.array(data['llm'])[~llm_mask], 
             '^', color='red', alpha=0.3, markersize=3, label='LLM Outliers')
    
    ax1.set_title('Individual Model Execution Time Changes (Outliers Highlighted)')
    ax1.set_xlabel('Test Case Number')
    ax1.set_ylabel('Execution Time (seconds)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Total execution time changes
    ax2 = axes[1]
    
    # Plot filtered total data
    ax2.plot(np.array(x)[total_mask], np.array(data['total'])[total_mask], 
             'o-', color='purple', alpha=0.7, linewidth=2, label='Total Time')
    
    # Add outlier points as small dots
    ax2.plot(np.array(x)[~total_mask], np.array(data['total'])[~total_mask], 
             'o', color='purple', alpha=0.3, markersize=3, label='Total Time Outliers')
    
    # Add mean line
    mean_total = np.mean(np.array(data['total'])[total_mask])  # Mean excluding outliers
    ax2.axhline(mean_total, color='red', linestyle='--', 
                label=f'Mean (filtered): {mean_total:.2f}s')
    
    ax2.set_title('Total Execution Time Changes (Outliers Highlighted)')
    ax2.set_xlabel('Test Case Number')
    ax2.set_ylabel('Total Execution Time (seconds)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add outlier statistics to the plot
    outlier_info = f"""Outlier Statistics:
PaddleOCR: {np.sum(~paddle_mask)} outliers removed
EasyOCR: {np.sum(~easy_mask)} outliers removed  
LLM: {np.sum(~llm_mask)} outliers removed
Total: {np.sum(~total_mask)} outliers removed"""
    
    fig.text(0.02, 0.02, outlier_info, fontsize=10, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('ocr_time_series_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Print outlier information
    print(f"\nOutlier Analysis:")
    print(f"PaddleOCR outliers removed: {np.sum(~paddle_mask)} ({np.sum(~paddle_mask)/len(data['paddleocr'])*100:.1f}%)")
    print(f"EasyOCR outliers removed: {np.sum(~easy_mask)} ({np.sum(~easy_mask)/len(data['easyocr'])*100:.1f}%)")
    print(f"LLM outliers removed: {np.sum(~llm_mask)} ({np.sum(~llm_mask)/len(data['llm'])*100:.1f}%)")
    print(f"Total time outliers removed: {np.sum(~total_mask)} ({np.sum(~total_mask)/len(data['total'])*100:.1f}%)")

def generate_analysis_report(data, viz_data):
    """Generate a comprehensive analysis report and save it to a text file."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
OCR 및 LLM 성능 분석 보고서
==========================================
생성 시간: {timestamp}
총 테스트 케이스 수: {len(data['total'])}개

1. 상세 통계 분석
==========================================
"""
    
    models = ['PaddleOCR', 'EasyOCR', 'LLM']
    times_data = [data['paddleocr'], data['easyocr'], data['llm']]
    
    # Detailed statistics table
    for model, times in zip(models, times_data):
        report += f"""
{model}:
  - 평균: {np.mean(times):.2f}초
  - 중앙값: {np.median(times):.2f}초
  - 최소값: {np.min(times):.2f}초
  - 최대값: {np.max(times):.2f}초
  - 표준편차: {np.std(times):.2f}초
  - 총합: {np.sum(times):.2f}초
"""
    
    # Total statistics
    report += f"""
총합:
  - 평균: {np.mean(data['total']):.2f}초
  - 중앙값: {np.median(data['total']):.2f}초
  - 최소값: {np.min(data['total']):.2f}초
  - 최대값: {np.max(data['total']):.2f}초
  - 표준편차: {np.std(data['total']):.2f}초
  - 총합: {np.sum(data['total']):.2f}초

2. 성능 비교 분석
==========================================
"""
    
    fastest_model = models[np.argmin(viz_data['avg_times'])]
    slowest_model = models[np.argmax(viz_data['avg_times'])]
    
    report += f"""
가장 빠른 모델: {fastest_model} ({np.min(viz_data['avg_times']):.2f}초)
가장 느린 모델: {slowest_model} ({np.max(viz_data['avg_times']):.2f}초)
성능 차이: {np.max(viz_data['avg_times']) - np.min(viz_data['avg_times']):.2f}초
평균 총 처리 시간: {np.mean(data['total']):.2f}초

3. 모델별 시간 비율
==========================================
"""
    
    for model, percentage in zip(models, viz_data['percentages']):
        report += f"{model}: {percentage:.1f}%\n"
    
    # Time range distribution analysis
    report += f"""
4. 시간대별 분포 분석
==========================================
"""
    
    time_ranges = [(0, 5), (5, 10), (10, 15), (15, float('inf'))]
    range_labels = ['5초 이하', '5-10초', '10-15초', '15초 이상']
    
    for i, (min_time, max_time) in enumerate(time_ranges):
        if max_time == float('inf'):
            count = sum(1 for t in data['total'] if t >= min_time)
        else:
            count = sum(1 for t in data['total'] if min_time <= t < max_time)
        percentage = count / len(data['total']) * 100
        report += f"{range_labels[i]}: {count}개 ({percentage:.1f}%)\n"
    
    # Performance insights
    report += f"""
5. 성능 인사이트
==========================================
"""
    
    # Function to filter outliers using IQR method
    def filter_outliers(times, factor=1.5):
        q1 = np.percentile(times, 25)
        q3 = np.percentile(times, 75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        mask = (times >= lower_bound) & (times <= upper_bound)
        return mask
    
    # Filter outliers for total time
    total_mask = filter_outliers(data['total'])
    filtered_total = np.array(data['total'])[total_mask]
    
    # Find the fastest and slowest test cases (excluding outliers)
    if len(filtered_total) > 0:
        fastest_case_idx = np.where(data['total'] == np.min(filtered_total))[0][0]
        slowest_case_idx = np.where(data['total'] == np.max(filtered_total))[0][0]
        
        report += f"""
가장 빠른 테스트 케이스 (특이값 제외, 케이스 #{fastest_case_idx + 1}):
  - 총 시간: {data['total'][fastest_case_idx]:.2f}초
  - PaddleOCR: {data['paddleocr'][fastest_case_idx]:.2f}초
  - EasyOCR: {data['easyocr'][fastest_case_idx]:.2f}초
  - LLM: {data['llm'][fastest_case_idx]:.2f}초

가장 느린 테스트 케이스 (특이값 제외, 케이스 #{slowest_case_idx + 1}):
  - 총 시간: {data['total'][slowest_case_idx]:.2f}초
  - PaddleOCR: {data['paddleocr'][slowest_case_idx]:.2f}초
  - EasyOCR: {data['easyocr'][slowest_case_idx]:.2f}초
  - LLM: {data['llm'][slowest_case_idx]:.2f}초
"""
    else:
        # Fallback to original method if no data after filtering
        fastest_case_idx = np.argmin(data['total'])
        slowest_case_idx = np.argmax(data['total'])
        
        report += f"""
가장 빠른 테스트 케이스 (케이스 #{fastest_case_idx + 1}):
  - 총 시간: {data['total'][fastest_case_idx]:.2f}초
  - PaddleOCR: {data['paddleocr'][fastest_case_idx]:.2f}초
  - EasyOCR: {data['easyocr'][fastest_case_idx]:.2f}초
  - LLM: {data['llm'][fastest_case_idx]:.2f}초

가장 느린 테스트 케이스 (케이스 #{slowest_case_idx + 1}):
  - 총 시간: {data['total'][slowest_case_idx]:.2f}초
  - PaddleOCR: {data['paddleocr'][slowest_case_idx]:.2f}초
  - EasyOCR: {data['easyocr'][slowest_case_idx]:.2f}초
  - LLM: {data['llm'][slowest_case_idx]:.2f}초
"""
    
    # Add outlier statistics
    outlier_count = np.sum(~total_mask)
    outlier_percentage = outlier_count / len(data['total']) * 100
    
    report += f"""
특이값 분석:
  - 제거된 특이값 수: {outlier_count}개 ({outlier_percentage:.1f}%)
  - 특이값 제거 후 평균: {np.mean(filtered_total):.2f}초
  - 특이값 제거 후 표준편차: {np.std(filtered_total):.2f}초

6. 권장사항
==========================================
"""
    
    # Performance recommendations
    if np.mean(data['paddleocr']) > np.mean(data['easyocr']):
        report += "- PaddleOCR가 EasyOCR보다 평균적으로 더 느리므로, EasyOCR 사용을 고려해보세요.\n"
    else:
        report += "- PaddleOCR가 EasyOCR보다 평균적으로 더 빠르므로, PaddleOCR 사용을 권장합니다.\n"
    
    if np.mean(data['llm']) > np.mean(data['paddleocr']) + np.mean(data['easyocr']):
        report += "- LLM 처리 시간이 OCR 처리 시간의 합보다 길므로, LLM 최적화를 고려해보세요.\n"
    
    if np.std(data['total']) > np.mean(data['total']) * 0.5:
        report += "- 총 처리 시간의 변동성이 높으므로, 일관성 있는 성능을 위한 추가 최적화가 필요합니다.\n"
    
    # Save report to file
    filename = f"ocr_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n분석 보고서가 '{filename}' 파일로 저장되었습니다.")
    
    return report

def main():
    """Main function"""
    file_path = "ocr_test_results.txt"
    
    try:
        # Extract data
        print("Extracting data from OCR test result file...")
        data = extract_performance_data(file_path)
        
        if not data['total']:
            print("No data extracted. Please check the file format.")
            return
        
        print(f"Extracted data from {len(data['total'])} test cases.")
        
        # Create visualizations
        print("\nCreating performance analysis visualizations...")
        viz_data = create_performance_visualizations(data)
        
        # Create time series analysis
        print("\nCreating time series analysis...")
        create_time_series_plot(data)
        
        # Generate and save analysis report
        print("\nGenerating comprehensive analysis report...")
        report = generate_analysis_report(data, viz_data)
        
        print("\nAnalysis completed!")
        print("- ocr_performance_analysis.png: Performance analysis charts")
        print("- ocr_time_series_analysis.png: Time series analysis charts")
        print("- ocr_analysis_report_YYYYMMDD_HHMMSS.txt: Detailed analysis report")
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 