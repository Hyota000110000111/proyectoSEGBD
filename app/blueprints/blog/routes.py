from . import blog_bp

@blog_bp.route('/')
def index():
    return "Blog Index"
