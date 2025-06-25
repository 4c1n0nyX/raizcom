from django.shortcuts import redirect

# =============== Función de Usuarios no autenticados ================ #
def no_autenticado(view_func):
    def wrapper_func (request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

# =============== Función de Usuarios Permitidos ================ #
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('403')
        return wrapper_func
    return decorator