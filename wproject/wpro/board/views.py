from django.shortcuts import render

# 메인페이지
def blish(request):
    return render(request,'blist.html')