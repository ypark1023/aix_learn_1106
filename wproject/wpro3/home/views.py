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
MODEL_PATH = os.path.join(settings.BASE_DIR, 'wmodel.joblib')
CSV_PATH = os.path.join(settings.BASE_DIR, '/data/wine.csv')

model = joblib.load(MODEL_PATH)

# Create your views here.
def index(request):
    return render(request,'index.html')

def adata(request):
    data = request.POST.get('data','10.5,6.1,3.35')

    # 파일 변환
    in_data = data
    in_data = in_data.split(',')
    in_data = [float(x) for x in data.split(',')]

    # 예측
    pred_array = model.predict([in_data])
    result2_num = pred_array[0]

    # [수정] decision_function 대신 predict_proba 사용 (shape: (1, 2) 형태의 2차원 배열 반환)
    proba_array = model.predict_proba([in_data])
    result_prob = np.round(proba_array[0], decimals=3)
    wine_list = ['White', 'Red']
    
    if result2_num == 0.0 or result2_num == 0:
        result2 = 'White'
        result3 = result_prob[0]
    elif result2_num == 1.0 or result2_num == 1:
        result2 = 'Red'
        result3 = result_prob[1]    
    else:
        result2 = 'Unknown'
        result3 = 0.0

    
    # 딕셔너리에 데이터 담기 (JsonResponse는 딕셔너리를 자동으로 JSON으로 변환)
    context = {
        'status': 'success',
        'result': in_data,       # 입력받은 특성값 리스트
        'result2': result2,      # 예측된 와인 이름 (문자열)
        'result3': float(result3), # 해당 와인의 확률 (파이썬 float 형변환 권장)
        'wine_list': wine_list,            # 와인 종류 리스트
        'probs': result_prob.tolist()    # 와인별 확률 리스트 (numpy array -> list 변환)
    }
    return JsonResponse(context)