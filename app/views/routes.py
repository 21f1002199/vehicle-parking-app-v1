# routes.py
from flask import Blueprint

import os
import matplotlib.pyplot as plt
from flask import current_app, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
from app.extensions import db, login_manager
from app.models import User, ParkingLot, ParkingSpot, Reservation
from app.forms import LoginForm, RegisterForm, EditProfileForm, ParkingLotForm, AdminProfileForm, SearchForm, ReservationForm, AdminSearchForm
from datetime import datetime
from collections import defaultdict, Counter
from werkzeug.security import check_password_hash, generate_password_hash


main = Blueprint('main', __name__)


def init_routes(app):

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @main.route('/')
    def home():
        return redirect(url_for('.login'))

    # ------------------ AUTH ------------------

    @main.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                password=generate_password_hash(form.password.data),
                role='user',
                full_name=form.full_name.data,
                email=form.email.data,
                phone_number=form.phone_number.data,
                address=form.address.data,
                pin_code=form.pin_code.data
            )
            db.session.add(user)
            db.session.commit()
            flash("User registered successfully.")
            return redirect(url_for('.login'))
        return render_template('register.html', form=form)

    @main.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                if user.role == 'admin':
                    return redirect(url_for('.admin_dashboard'))
                else:
                    return redirect(url_for('.user_dashboard'))
            flash("Invalid credentials")
        return render_template('login.html', form=form)

    @main.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('.login'))

    # ------------------ ADMIN ------------------

    @main.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))
        lots = ParkingLot.query.all()
        users = User.query.filter_by(role='user').all()
        return render_template('admin_dashboard.html', lots=lots, users=users)

    @main.route('/admin/create_lot', methods=['GET', 'POST'])
    @login_required
    def create_lot():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))
        form = ParkingLotForm()
        if form.validate_on_submit():
            lot = ParkingLot(
                name=form.name.data,
                address=form.address.data,
                pin_code=form.pin_code.data,
                price=form.price.data,
                max_spots=form.max_spots.data
            )
            db.session.add(lot)
            db.session.commit()

            for i in range(1, form.max_spots.data + 1):
                spot = ParkingSpot(lot_id=lot.id, spot_number=i, status='A')
                db.session.add(spot)
            db.session.commit()

            flash("Parking lot created with spots.")
            return redirect(url_for('.admin_dashboard'))
        return render_template('create_lot.html', form=form)


    @main.route('/admin/lot/<int:lot_id>/spots')
    @login_required
    def view_lot_spots(lot_id):
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        lot = ParkingLot.query.get_or_404(lot_id)
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        return render_template('lot_spots.html', lot=lot, spots=spots)


    @main.route('/admin/delete_lot/<int:lot_id>')
    @login_required
    def delete_lot(lot_id):
        if current_user.role != 'admin':
            return redirect(url_for('.login'))
        lot = ParkingLot.query.get_or_404(lot_id)
        if any(spot.status == 'O' for spot in lot.spots):
            flash("Cannot delete lot with occupied spots.")
            return redirect(url_for('.admin_dashboard'))
        for spot in lot.spots:
            db.session.delete(spot)
        db.session.delete(lot)
        db.session.commit()
        flash("Parking lot deleted.")
        return redirect(url_for('.admin_dashboard'))

    @main.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
    @login_required
    def edit_lot(lot_id):
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        lot = ParkingLot.query.get_or_404(lot_id)
        form = ParkingLotForm(obj=lot)

        if form.validate_on_submit():
        # Update basic fields
            lot.name = form.name.data
            lot.address = form.address.data
            lot.pin_code = form.pin_code.data
            lot.price = form.price.data

            new_max_spots = form.max_spots.data
            current_spot_count = ParkingSpot.query.filter_by(lot_id=lot.id).count()

            if new_max_spots > current_spot_count:
            # Add new available spots
                for i in range(current_spot_count + 1, new_max_spots + 1):
                    new_spot = ParkingSpot(lot_id=lot.id, spot_number=i, status='A')
                    db.session.add(new_spot)

            elif new_max_spots < current_spot_count:
            # Safely remove only available spots
                removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A')\
                                                    .limit(current_spot_count - new_max_spots)\
                                                    .all()
                if len(removable_spots) < (current_spot_count - new_max_spots):
                    flash('Cannot reduce spots — not enough available (some are occupied).', 'danger')
                    return redirect(url_for('edit_lot', lot_id=lot.id))

                for spot in removable_spots:
                    db.session.delete(spot)

            remaining_spots = ParkingSpot.query.filter_by(lot_id=lot.id).order_by(ParkingSpot.id).all()
            for index, spot in enumerate(remaining_spots, start=1):
                spot.spot_number = index

            # Finally update the max_spots field
            lot.max_spots = new_max_spots

            db.session.commit()
            flash('Lot updated successfully.', 'success')
            return redirect(url_for('.admin_dashboard'))

        return render_template('edit_lot.html', form=form, lot=lot)


    @main.route('/admin/profile', methods=['GET', 'POST'])
    @login_required
    def admin_profile():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))
        form = AdminProfileForm(obj=current_user)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.full_name = form.full_name.data
            current_user.address = form.address.data
            current_user.pin_code = form.pin_code.data
            if form.password.data:
                current_user.password = form.password.data
            db.session.commit()
            flash("Profile updated.")
            return redirect(url_for('.admin_profile'))
        return render_template('admin_profile.html', form=form)


    @main.route('/admin/users')
    @login_required
    def admin_users():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        users = User.query.filter_by(role='user').all()

        return render_template('admin_users.html', users=users)


    
    @main.route('/admin/user/<int:user_id>/records')
    @login_required
    def admin_user_records(user_id):
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        user = User.query.get_or_404(user_id)

        # Current active reservation (no end_time)
        current_reservation = Reservation.query.filter_by(user_id=user.id, end_time=None).first()

        # Past reservations (with end_time)
        reservation_history = Reservation.query.filter(
            Reservation.user_id == user.id,
            Reservation.end_time.isnot(None)
        ).order_by(Reservation.start_time.desc()).all()

        return render_template(
            'admin_user_records.html',
            user=user,
            current_reservation=current_reservation,
            reservation_history=reservation_history
        )





    
    @main.route('/admin/search', methods=['GET', 'POST'])
    @login_required
    def admin_search():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        form = AdminSearchForm()
        user_results = []
        lot_results = []

        if form.validate_on_submit():
            query = form.query.data.strip()
            if form.search_in.data == 'users':
                user_results = User.query.filter(User.username.ilike(f"%{query}%")).all()
            elif form.search_in.data == 'lots':
                lots = ParkingLot.query.filter(
                    (ParkingLot.address.ilike(f"%{query}%")) |
                    (ParkingLot.pin_code.ilike(f"%{query}%"))
                ).all()
                for lot in lots:
                    total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
                    available = sum(1 for s in total_spots if s.status == 'A')
                    occupied = sum(1 for s in total_spots if s.status == 'O')
                    lot_results.append({
                        'lot': lot,
                        'available': available,
                        'occupied': occupied
                    })

        return render_template('admin_search.html', form=form, user_results=user_results, lot_results=lot_results)





    @main.route('/admin/summary')
    @login_required
    def admin_summary():
        if current_user.role != 'admin':
            return redirect(url_for('.login'))

        # Get month and year from query parameters or default to current
        selected_month = request.args.get('month', datetime.now().month, type=int)
        selected_year = request.args.get('year', datetime.now().year, type=int)

        lots = ParkingLot.query.all()
        summary_data = []
        pie_paths = []
        bar_labels = []
        bar_values = []
        
        chart_dir = os.path.join(current_app.root_path, 'static', 'summary_charts')
        os.makedirs(chart_dir, exist_ok=True)

        # Clear old charts
        for filename in os.listdir(chart_dir):
            file_path = os.path.join(chart_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Filter by month/year
        start_date = datetime(selected_year, selected_month, 1)
        if selected_month == 12:
            end_date = datetime(selected_year + 1, 1, 1)
        else:
            end_date = datetime(selected_year, selected_month + 1, 1)

        for lot in lots:
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            available_spots = total_spots - occupied_spots

            # Pie Chart
            pie_labels = ['Occupied', 'Vacant']
            pie_sizes = [occupied_spots, available_spots]
            pie_colors = ['#ff4d4d', '#28a745']

            plt.figure(figsize=(9,9))
            plt.pie(pie_sizes, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%', startangle=140, textprops={'fontsize': 23, 'weight': 'bold'}, labeldistance=1.1)
            plt.axis('equal')
            pie_filename = f'lot_{lot.id}_pie.png'
            pie_path = os.path.join(chart_dir, pie_filename)
            plt.savefig(pie_path)
            pie_paths.append(pie_filename)
            plt.close()


            query = Reservation.query.join(ParkingSpot).filter(ParkingSpot.lot_id == lot.id)

            if selected_month and selected_year:
                try:
                    query = query.filter(
                    db.extract('month', Reservation.start_time) == selected_month,
                    db.extract('year', Reservation.end_time) == selected_year
                    )
                except ValueError:
                    pass


            # Revenue filtered by month/year
            revenue = db.session.query(db.func.sum(Reservation.cost)).filter(
                Reservation.spot_id.in_(
                    db.session.query(ParkingSpot.id).filter_by(lot_id=lot.id)
                ),
                Reservation.end_time >= start_date,
                Reservation.end_time < end_date
            ).scalar() or 0

            reservation_count = query.count()

            bar_labels.append(lot.name)
            bar_values.append(revenue)

            summary_data.append({
                'lot': lot,
                'occupied': occupied_spots,
                'vacant': available_spots,
                'revenue': round(revenue, 2),
                'reservation_count': reservation_count
            })

        # Bar Chart
        plt.figure(figsize=(8, 4))
        bars = plt.bar(bar_labels, bar_values, color='#007bff')
        plt.ylabel('Revenue (₹)')
        plt.title(f'Revenue per Lot – {start_date.strftime("%B %Y")}')
        plt.xticks(rotation=45)
        plt.tight_layout()

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height, f'₹{height:.2f}',
                     ha='center', va='bottom', fontsize=9, fontweight='bold')

        bar_chart_filename = 'revenue_bar.png'
        bar_chart_path = os.path.join(chart_dir, bar_chart_filename)
        plt.savefig(bar_chart_path)
        plt.close()

        total_revenue = sum(bar_values)

        return render_template(
            'admin_summary.html',
            summary_data=summary_data,
            pie_paths=pie_paths,
            bar_chart=bar_chart_filename,
            total_revenue=round(total_revenue, 2),
            selected_month=selected_month,
            selected_year=selected_year
        )







    # ------------------ USER ------------------

    @main.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if current_user.role != 'user':
            return redirect(url_for('.login'))

        lots = ParkingLot.query.all()
        lot_data = []
        for lot in lots:
            available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
            lot_data.append({'lot': lot, 'available_spots': available_spots})                                       
        current_reservations = Reservation.query.filter_by(user_id=current_user.id).filter(Reservation.end_time == None).all()

        past_reservations = Reservation.query.filter_by(user_id=current_user.id).filter(Reservation.end_time != None, Reservation.user_deleted == False).all()

        return render_template(
            'user_dashboard.html',
            lot_data=lot_data,
            current_reservations=current_reservations,
            past_reservations=past_reservations
        )


    @main.route('/user/delete_history/<int:reservation_id>', methods=['POST'])
    @login_required
    def delete_history(reservation_id):
        reservation = Reservation.query.get_or_404(reservation_id)
        if reservation.user_id != current_user.id or reservation.end_time is None:
            flash("Unauthorized or invalid request.")
            return redirect(url_for('.user_dashboard'))
        reservation.user_deleted = True
        db.session.commit()
        flash("Reservation deleted from history.")
        return redirect(url_for('.user_dashboard'))

    @main.route('/user/delete_all_history', methods=['POST'])
    @login_required
    def delete_all_history():
        reservations = Reservation.query.filter_by(user_id=current_user.id).filter(
            Reservation.end_time != None
        ).all()
        for r in reservations:
            r.user_deleted = True
        db.session.commit()
        flash("All reservations removed from your history.")
        return redirect(url_for('.user_dashboard'))




    @main.route('/user/reserve/<int:lot_id>', methods=['GET', 'POST'])
    @login_required
    def reserve(lot_id):
        if current_user.role != 'user':
            return redirect(url_for('.login'))

        spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
        if not spot:
            flash("No available spots.")
            return redirect(url_for('.user_dashboard'))

        form = ReservationForm(
            spot_id=spot.id,
            lot_id=lot_id,
            user_id=current_user.id
        )

        if form.validate_on_submit():
            spot.status = 'O'
            reservation = Reservation(
                user_id=current_user.id,
                spot_id=spot.id,
                start_time=datetime.now(),
                end_time=None,
                cost=0.0,
                vehicle_number=form.vehicle_number.data  # Add this column to Reservation model
            )
            db.session.add(reservation)
            db.session.commit()
            flash("Spot reserved.")
            return redirect(url_for('.user_dashboard'))

        return render_template('reserve_form.html', form=form)


    @main.route('/user/release/<int:reservation_id>', methods=['GET', 'POST'])
    @login_required
    def release(reservation_id):
        if current_user.role != 'user':
            return redirect(url_for('.login'))

        reservation = Reservation.query.get_or_404(reservation_id)
        if reservation.user_id != current_user.id:
            flash("Unauthorized.")
            return redirect(url_for('.user_dashboard'))

        if request.method == 'POST':
            reservation.end_time = datetime.now()
            duration = (reservation.end_time - reservation.start_time).total_seconds() / 3600
            spot = ParkingSpot.query.get(reservation.spot_id)
            lot = ParkingLot.query.get(spot.lot_id)
            reservation.cost = round(duration * lot.price, 2)
            spot.status = 'A'
            db.session.commit()
            flash(f"Spot released. Total cost: ₹{reservation.cost}")
            return redirect(url_for('.user_dashboard'))

        # GET request → show confirmation page
        now = datetime.now()
        duration = (now - reservation.start_time).total_seconds() / 3600
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)
        cost = round(duration * lot.price, 2)
        hours = int(duration)
        minutes = int((duration - hours) * 60)

        return render_template(
            'confirm_release.html',
            reservation=reservation,
            lot=lot,
            duration=f"{hours}h {minutes}m",
            cost=cost
        )





    @main.route('/user/summary')
    @login_required
    def user_summary():
        if current_user.role != 'user':
            return redirect(url_for('.login'))

        selected_month = request.args.get('month', datetime.now().month, type=int)
        selected_year = request.args.get('year', datetime.now().year, type=int)

        # Filter reservations for current user within selected month/year
        from sqlalchemy import and_, extract
        reservations = Reservation.query.filter(
            and_(
                Reservation.user_id == current_user.id,
                Reservation.end_time.isnot(None),
                extract('month', Reservation.start_time) == selected_month,
                extract('year', Reservation.start_time) == selected_year
            )
        ).all()

        total_cost = sum(res.cost for res in reservations if res.cost)
        total_seconds = sum((r.end_time - r.start_time).total_seconds() for r in reservations)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        total_reservations = len(reservations)
        lots_explored = len(set(r.spot.lot_id for r in reservations))

    # Pie chart - spending per lot
        lot_expenditure = defaultdict(float)
        for r in reservations:
            if r.cost:
                lot_expenditure[r.spot.lot.name] += r.cost

        chart_dir = os.path.join(current_app.root_path, 'static', 'user_summary_charts')
        os.makedirs(chart_dir, exist_ok=True)
        for f in os.listdir(chart_dir):
            os.remove(os.path.join(chart_dir, f))

    # PIE chart
        pie_labels = list(lot_expenditure.keys())
        pie_values = list(lot_expenditure.values())
        pie_colors = plt.cm.Paired.colors

        plt.figure()
        plt.pie(pie_values, labels=pie_labels, colors=pie_colors, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        pie_chart_path = os.path.join(chart_dir, 'pie_chart.png')
        plt.savefig(pie_chart_path)
        plt.close()

        lot_reservation_counts = Counter(r.spot.lot.name for r in reservations)

        plt.figure(figsize=(5, 6))
        plt.bar(lot_reservation_counts.keys(), lot_reservation_counts.values(), color='skyblue', edgecolor='black')
        plt.title(f'Reservations per Lot in {selected_month}-{selected_year}')
        plt.xlabel('Lot')
        plt.ylabel('Number of Reservations')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        bar_chart_path = os.path.join(chart_dir, 'bar_chart.png')
        plt.savefig(bar_chart_path)
        plt.close()

        return render_template(
            'user_summary.html',
            reservations=reservations,
            total_cost=round(total_cost, 2),
            total_duration=f"{hours}h {minutes}m",
            total_reservations=total_reservations,
            lots_explored=lots_explored,
            pie_chart='pie_chart.png',
            line_chart='bar_chart.png',
            selected_month=selected_month,
            selected_year=selected_year
        )




    





    @main.route('/user/search', methods=['GET', 'POST'])
    @login_required
    def user_search():
        lot_data = []
        if request.method == 'POST':
            query = request.form.get('pin', '').strip()
            if query:
                matching_lots = ParkingLot.query.filter(
                    (ParkingLot.pin_code.ilike(f'%{query}%')) |
                    (ParkingLot.address.ilike(f'%{query}%'))
                ).all()

                for lot in matching_lots:
                    available_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
                    lot_data.append({'lot': lot, 'available_spots': available_spots})
    
        return render_template('user_search.html', lot_data=lot_data)


    @main.route('/user/profile', methods=['GET', 'POST'])
    @login_required
    def user_profile():
        if current_user.role != 'user':
            return redirect(url_for('.login'))

        form = EditProfileForm(obj=current_user)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.full_name = form.full_name.data
            current_user.address = form.address.data
            current_user.pin_code = form.pin_code.data
            current_user.email = form.email.data
            current_user.phone_number = form.phone_number.data
            if form.password.data:
                current_user.password = generate_password_hash(form.password.data)
            db.session.commit()
            flash('Profile updated.')
            return redirect(url_for('.user_dashboard'))

        return render_template('user_profile.html', form=form)




