from flask import request, render_template, session, flash, redirect, url_for, Blueprint


admin_rt = Blueprint("admin_rt", __name__, url_prefix='/')

@admin_rt.route("/admin/dashboard")
def dashboard():
    if 'user_role' not in session or session['user_role'] != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('admin/dashboard.html')
    