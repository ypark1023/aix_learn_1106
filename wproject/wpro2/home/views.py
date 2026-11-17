import os
import json
import joblib
import numpy as np # numpy 확인
import pandas as pd # pandas 인
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from scipy.special import softmax
import traceback

# MODEL_PATH = os.path.join(settings.BASE_DIR, 'model.joblib')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model3.joblib')
CSV_PATH = os.path.join(settings.BASE_DIR, '/static/data/fish_logistic.csv')

model = joblib.load(MODEL_PATH)

# Create your views here.
def ajax_data(request):
    data = request.POST.get('data','242.0,25.4,30.0,11.52,4.0200')

    # 파일 변환
    in_data = data
    in_data = in_data.split(',')
    in_data = [float(x) for x in data.split(',')]

    # 예측
    pred_array = model.predict([in_data])
    result2 = pred_array[0]
    decisions = model.decision_function([in_data])
    soft1 = softmax(decisions,axis=1)
    result_prob = np.round(soft1,decimals=3)[0]

    species_list = ['Bream', 'Parkki', 'Perch', 'Pike', 'Roach', 'Smelt', 'Whitefish']
    
    if result2 == 'Bream':
        result3 = result_prob[0]
    elif result2 == 'Parkki':
        result3 = result_prob[1]    
    elif result2 == 'Perch':
        result3 = result_prob[2]    
    elif result2 == 'Pike':
        result3 = result_prob[3]    
    elif result2 == 'Roach':
        result3 = result_prob[4]    
    elif result2 == 'Smelt':
        result3 = result_prob[5]    
    elif result2 == 'Whitefish':
        result3 = result_prob[6]    

    
    # 딕셔너리에 데이터 담기 (JsonResponse는 딕셔너리를 자동으로 JSON으로 변환)
    context = {
        'status': 'success',
        'result': in_data,       # 입력받은 특성값 리스트
        'result2': result2,      # 예측된 품종 이름 (문자열)
        'result3': float(result3), # 해당 품종의 확률 (파이썬 float 형변환 권장)
        'species_list': species_list,            # 7개 생선 이름 리스트
        'probs': result_prob.tolist()    # 7개 품종별 확률 리스트 (numpy array -> list 변환)
    }
    return JsonResponse(context)


# 메인페이지
def index(request):
    return render(request,'index.html')
