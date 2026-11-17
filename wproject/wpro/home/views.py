import os
import json
import joblib
import numpy as np # numpy 임포트 확인
import pandas as pd # pandas 임포트 확인
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import traceback

# MODEL_PATH = os.path.join(settings.BASE_DIR, 'model.joblib')
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model2.joblib')
CSV_PATH = os.path.join(settings.BASE_DIR, 'perch_full.csv')

model = joblib.load(MODEL_PATH)

perch_weight = [
    5.9, 32.0, 40.0, 51.5, 70.0, 100.0, 78.0, 80.0, 85.0, 85.0,
    110.0, 115.0, 125.0, 130.0, 120.0, 120.0, 130.0, 135.0, 110.0,
    130.0, 150.0, 145.0, 150.0, 170.0, 225.0, 145.0, 188.0, 180.0,
    197.0, 218.0, 300.0, 260.0, 265.0, 250.0, 250.0, 300.0, 320.0,
    514.0, 556.0, 840.0, 685.0, 700.0, 700.0, 690.0, 900.0, 650.0,
    820.0, 850.0, 900.0, 1015.0, 820.0, 1100.0, 1000.0, 1100.0,
    1000.0, 1000.0
]



#Species	Weight,Length,Diagonal,Height,Width
#0	Bream	242.0,25.4,30.0,11.52,4.0200
#1	Bream	290.0,26.3,31.2,12.48,4.3056

# 퀴즈 버전 ########################################     

def ajax_data(request):
    data = request.POST.get('data','242.0,25.4,30.0,11.52,4.0200')

    # 파일 변환
    in_data = data
    in_data = in_data.split(',')
    result = list(map(float,in_data))

    # 예측
    print('입력데이터 : ',result)
    result = model.predict([result])
    print(f'예측생선 : {result[0]} g')
    # 파일전달
    context = {
        'result_data':f'{result}','result':'success'
    }
    return JsonResponse(context)


# 메인페이지
def index(request):
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # model = joblib.load(BASE_DIR / "model.joblib")
    # # 예측
    # in_data = '40,11.73,7.22'
    # in_data = in_data.split(',')
    # result = list(map(float,in_data))

    #예측
    # print('입력데이터 : ',result)
    # result = model.predict([result])
    # print(f'예측무게 : {result[0]:.2f} g')
    # print("주소 : ",BASE_DIR)

    return render(request,'index.html')




# 수업 버전 ########################################     

# def ajax_data(request):
#     data = request.POST.get('data','40,11.73,7.22')
#     BASE_DIR = Path(__file__).resolve().parent.parent
#     model = joblib.load(BASE_DIR / "model.joblib")
    
#     # 파일 변환
#     in_data = data
#     in_data = in_data.split(',')
#     result = list(map(float,in_data))

#     # 예측
#     print('입력데이터 : ',result)
#     result = model.predict([result])
#     print(f'예측무게 : {result[0]:.2f} g')
#     # 파일전달
#     context = {
#         'result_data':f'{result[0]:.2f}','result':'success'
#     }
#     return JsonResponse(context)


# # 메인페이지
# def index(request):
#     # BASE_DIR = Path(__file__).resolve().parent.parent
#     # model = joblib.load(BASE_DIR / "model.joblib")
#     # # 예측
#     # in_data = '40,11.73,7.22'
#     # in_data = in_data.split(',')
#     # result = list(map(float,in_data))

#     #예측
#     # print('입력데이터 : ',result)
#     # result = model.predict([result])
#     # print(f'예측무게 : {result[0]:.2f} g')
#     # print("주소 : ",BASE_DIR)

#     return render(request,'index.html')




# 그래프 있는 버전 ########################################     
# def index(request):
#     df = pd.read_csv(CSV_PATH)
#     df.columns = df.columns.str.strip()

#     base_fish_data = []
#     for idx, row in df.iterrows():
#         base_fish_data.append({
#             'x': float(row['length']),
#             'y': float(perch_weight[idx]),
#             'height': float(row['height']),
#             'width': float(row['width'])
#         })

#     context = {
#         'base_fish_data': base_fish_data
#     }
#     return render(request, 'index.html', context)


# def predict_weight(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             length = float(data.get('length'))
#             height = float(data.get('height'))
#             width = float(data.get('width'))

#             # DataFrame 대신 2차원 NumPy 배열로 전달하여 컬럼명 불일치 에러 원천 차단
#             input_array = np.array([[length, height, width]])
            
#             predicted = model.predict(input_array)[0]
#             final_weight = round(max(0.0, float(predicted)), 1)

#             return JsonResponse({'status': 'success', 'weight': final_weight})
        
#         except Exception as e:
#             print("=== 예측 에러 발생 ===")
#             traceback.print_exc()
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#     return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)



# 그래프 없는 버전 ########################################        
# import os
# import json
# import joblib
# import numpy as np
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.conf import settings

# # 서버 시작 시 학습된 파이프라인 모델 로드 (manage.py와 같은 폴더에 model.joblib 있음)
# MODEL_PATH = os.path.join(settings.BASE_DIR, 'model.joblib')
# model = joblib.load(MODEL_PATH)

# def index(request):
#     return render(request, 'index.html')


# # 예측
# # input1 = [40.0,11.73,7.22]
# # input1 = [22.0,6.11,3.41]
# # input1 = input('생선 길이/높이/두깨(예:19.6,5.14,3.04)')

# # 입력받은 길이, 높이, 두께로 무게를 예측해 JSON으로 반환하는 API
# def predict_weight(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             length = float(data.get('length'))
#             height = float(data.get('height'))
#             width = float(data.get('width'))

#             # 파이프라인 모델 입력 형태에 맞게 2차원 배열로 변환: [[length, height, width]]
#             input_features = np.array([[length, height, width]])
            
#             # 예측 수행 (PolynomialFeatures -> StandardScaler -> Ridge 자동 통과)
#             predicted = model.predict(input_features)[0]

#             # 무게가 음수로 나오는 경우 0으로 보정하고 소수점 첫째 자리까지 반올림
#             final_weight = round(max(0.00, float(predicted)), 2)

#             return JsonResponse({'status': 'success', 'weight': final_weight})
        
#         except (ValueError, TypeError, KeyError) as e:
#             return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#     return JsonResponse({'status': 'error', 'message': 'POST 요청만 허용됩니다.'}, status=405)