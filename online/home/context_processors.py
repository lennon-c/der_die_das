from der_die_das.forms import  ByLemmaForm  # type: ignore

def add_search_form(request):
    return {'search_form': ByLemmaForm()}