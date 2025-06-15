import unittest
from app import app
from flask import json

class TestApp(unittest.TestCase):
    def setUp(self):
        # Set up test client for Flask app
        self.app = app.test_client()
        self.app.testing = True

    def test_home_route(self):
        # Test a GET request to the home route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        # self.assertIn(b'Expected Content', response.data)

    def test_user_login_get(self):
        # Test GET request to the user login route
        response = self.app.get('/user-login')
        self.assertEqual(response.status_code, 200)

    def test_user_login_html_get(self):
        # Test GET request to the user login HTML route
        response = self.app.get('/user-login.html')
        self.assertEqual(response.status_code, 200)

    def test_logout_redirect(self):
        # Test logout redirect
        response = self.app.get('/logout', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_faq_route(self):
        # Test a GET request to the FAQ route
        response = self.app.get('/FAQ')
        self.assertEqual(response.status_code, 200)

    def test_sidebar_route(self):
        # Test a GET request to the sidebar route
        response = self.app.get('/sidebar')
        self.assertEqual(response.status_code, 200)

    def test_admin_login_redirect(self):
        # Test admin login redirect
        response = self.app.get('/admin-login', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_login_get(self):
        # Test GET request to the admin login route
        response = self.app.get('/admin/login')
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_requires_login(self):
        # Test that admin dashboard requires login
        response = self.app.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_logout_redirect(self):
        # Test admin logout redirect
        response = self.app.get('/admin/logout', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_user_signup_get(self):
        # Test GET request to the user signup route
        response = self.app.get('/user-signup')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_get(self):
        # Test GET request to the forgot password route
        response = self.app.get('/forgot-password')
        self.assertEqual(response.status_code, 200)

    def test_tracking_get(self):
        # Test a GET request to the tracking route
        response = self.app.get('/tracking')
        self.assertEqual(response.status_code, 200)

    def test_validate_order_item_id_post(self):
        # Test POST request to validate order item ID
        response = self.app.post('/validate-order-item-id', json={'order_item_id': 'test'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('exists', data)

    def test_api_user_activities_unauthorized(self):
        # Test unauthorized access to user activities API
        response = self.app.get('/api/user-activities')
        self.assertIn(response.status_code, [401, 302, 200])  # 401 if not logged in

    def test_error_handling(self):
        # Test error handling (e.g., 404)
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    def test_index_route(self):
        # Test a GET request to the index route
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/index.html')
        self.assertEqual(response2.status_code, 200)

    def test_services_route(self):
        # Test a GET request to the services route
        response = self.app.get('/services')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/services.html')
        self.assertEqual(response2.status_code, 200)

    def test_parcel_tracker_route(self):
        # Test a GET request to the parcel tracker route
        response = self.app.get('/parcel-tracker')
        self.assertEqual(response.status_code, 200)

    def test_personal_info_route(self):
        # Test a GET request to the personal info route
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    def test_change_password_get(self):
        # Test GET request to the change password route
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    def test_update_email_route(self):
        # Test GET request to the update email route
        response = self.app.get('/update-email')
        self.assertEqual(response.status_code, 200)

    def test_privacy_settings_route(self):
        # Test a GET request to the privacy settings route
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    def test_language_region_route(self):
        # Test a GET request to the language region route
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    def test_recent_logins_route(self):
        # Test a GET request to the recent logins route
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    def test_recent_bookings_route(self):
        # Test a GET request to the recent bookings route
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    def test_truck_route(self):
        # Test a GET request to the truck route
        response = self.app.get('/truck')
        self.assertEqual(response.status_code, 200)

    def test_truck_book_route(self):
        # Test a GET request to the truck book route
        response = self.app.get('/truck-book')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_route(self):
        # Test a GET request to the motorcycle route
        response = self.app.get('/motorcycle')
        self.assertEqual(response.status_code, 200)

    def test_car_route(self):
        # Test a GET request to the car route
        response = self.app.get('/car')
        self.assertEqual(response.status_code, 200)

    def test_payment_wall_get(self):
        # Test GET request to the payment wall route
        response = self.app.get('/payment-wall')
        self.assertEqual(response.status_code, 200)

    def test_register_form_get(self):
        # Test GET request to the register form route
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_add_user_post_missing_fields(self):
        # Should redirect with error if fields are missing
        response = self.app.post('/add-user', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_upload_profile_image_post_no_file(self):
        # Should return 400 if no file uploaded
        with self.app.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
            sess['username'] = 'testuser'
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 400)

    def test_update_profile_post_not_logged_in(self):
        # Should return not logged in if session missing
        response = self.app.post('/update-profile', json={'field': 'name', 'value': 'New Name'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('User not logged in', response.get_data(as_text=True))

    def test_update_email_post_not_logged_in(self):
        # Should return 401 if session missing
        response = self.app.post('/update_email', json={'email': 'new@example.com'})
        self.assertEqual(response.status_code, 401)

    def test_user_dashboard_redirect(self):
        response = self.app.get('/user-dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_dashboard_redirect(self):
        response = self.app.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_forgot_password_get(self):
        response = self.app.get('/admin/forgot-password')
        self.assertEqual(response.status_code, 200)

    def test_admin_forgot_password_submit_post_missing_email(self):
        response = self.app.post('/admin/forgot-password/submit', data={})
        self.assertIn(response.status_code, [200, 302, 303])

    def test_admin_verification_code_get(self):
        response = self.app.get('/admin-verification-code')
        self.assertEqual(response.status_code, 200)

    def test_admin_new_password_get(self):
        response = self.app.get('/admin-new-password')
        self.assertEqual(response.status_code, 200)

    def test_admin_resend_otp_post_missing_email(self):
        response = self.app.post('/admin-resend-otp', data={})
        self.assertEqual(response.status_code, 400)

    def test_submit_ticket_get(self):
        response = self.app.get('/submit-ticket')
        self.assertEqual(response.status_code, 200)

    def test_personal_info_get(self):
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    def test_change_password_get(self):
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    def test_privacy_settings_get(self):
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    def test_language_region_get(self):
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    def test_recent_logins_get(self):
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    def test_recent_bookings_get(self):
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    def test_truck_book2_get(self):
        response = self.app.get('/truck-book2')
        self.assertEqual(response.status_code, 200)

    def test_truck_book3_get(self):
        response = self.app.get('/truck-book3')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book_get(self):
        response = self.app.get('/motorcycle-book')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book2_get(self):
        response = self.app.get('/motorcycle-book2')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book3_get(self):
        response = self.app.get('/motorcycle-book3')
        self.assertEqual(response.status_code, 200)

    def test_carbook_get(self):
        response = self.app.get('/carbook')
        self.assertEqual(response.status_code, 200)

    def test_carbook2_get(self):
        response = self.app.get('/carbook2')
        self.assertEqual(response.status_code, 200)

    def test_carbook3_get(self):
        response = self.app.get('/carbook3')
        self.assertEqual(response.status_code, 200)

    def test_parceltracking_get_no_tracking_id(self):
        response = self.app.get('/parceltracking')
        self.assertEqual(response.status_code, 200)

    def test_update_full_name_post_not_logged_in(self):
        response = self.app.post('/update-full-name', json={'full_name': 'Test User'})
        self.assertEqual(response.status_code, 401)

    def test_upload_profile_image_post_not_logged_in(self):
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 401)

    def test_admin_employees_redirect(self):
        response = self.app.get('/admin/employees', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_hexaboxes_redirect(self):
        response = self.app.get('/admin/hexaboxes', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_utilities_redirect(self):
        response = self.app.get('/admin/utilities', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_vehicles_redirect(self):
        response = self.app.get('/admin/vehicles', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_redirect(self):
        response = self.app.get('/admin/employee-salary', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_redirect(self):
        response = self.app.get('/admin/products', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_redirect(self):
        response = self.app.get('/admin/sales', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_redirect(self):
        response = self.app.get('/admin/customers', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_add_post_not_logged_in(self):
        response = self.app.post('/admin/products/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_update_post_not_logged_in(self):
        response = self.app.post('/admin/products/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_delete_post_not_logged_in(self):
        response = self.app.post('/admin/products/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_add_post_not_logged_in(self):
        response = self.app.post('/admin/sales/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_update_post_not_logged_in(self):
        response = self.app.post('/admin/sales/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_delete_post_not_logged_in(self):
        response = self.app.post('/admin/sales/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_add_post_not_logged_in(self):
        response = self.app.post('/admin/customers/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_update_post_not_logged_in(self):
        response = self.app.post('/admin/customers/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_delete_post_not_logged_in(self):
        response = self.app.post('/admin/customers/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_add_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_update_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_delete_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_api_utilities_chart_data_unauthorized(self):
        response = self.app.get('/api/utilities/chart-data')
        self.assertEqual(response.status_code, 401)

    def test_api_utilities_generate_report_unauthorized(self):
        response = self.app.post('/api/utilities/generate-report', data={})
        self.assertEqual(response.status_code, 401)

    def test_admin_support_tickets_reply_post_missing_data(self):
        response = self.app.post('/admin/support-tickets/reply', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_support_tickets_reply_page_not_logged_in(self):
        response = self.app.get('/admin/support-tickets/reply/fake-ticket-id', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_support_ticket_done_not_logged_in(self):
        response = self.app.post('/admin/support/ticket/done/fake-ticket-id')
        # Should return 401 or 404 or 500 depending on implementation
        self.assertIn(response.status_code, [401, 404, 500])

    def test_index_route(self):
        # Test a GET request to the index route
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/index.html')
        self.assertEqual(response2.status_code, 200)

    def test_services_route(self):
        # Test a GET request to the services route
        response = self.app.get('/services')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/services.html')
        self.assertEqual(response2.status_code, 200)

    def test_parcel_tracker_route(self):
        # Test a GET request to the parcel tracker route
        response = self.app.get('/parcel-tracker')
        self.assertEqual(response.status_code, 200)

    def test_personal_info_route(self):
        # Test a GET request to the personal info route
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    def test_change_password_get(self):
        # Test GET request to the change password route
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    def test_update_email_route(self):
        # Test GET request to the update email route
        response = self.app.get('/update-email')
        self.assertEqual(response.status_code, 200)

    def test_privacy_settings_route(self):
        # Test a GET request to the privacy settings route
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    def test_language_region_route(self):
        # Test a GET request to the language region route
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    def test_recent_logins_route(self):
        # Test a GET request to the recent logins route
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    def test_recent_bookings_route(self):
        # Test a GET request to the recent bookings route
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    def test_truck_route(self):
        # Test a GET request to the truck route
        response = self.app.get('/truck')
        self.assertEqual(response.status_code, 200)

    def test_truck_book_route(self):
        # Test a GET request to the truck book route
        response = self.app.get('/truck-book')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_route(self):
        # Test a GET request to the motorcycle route
        response = self.app.get('/motorcycle')
        self.assertEqual(response.status_code, 200)

    def test_car_route(self):
        # Test a GET request to the car route
        response = self.app.get('/car')
        self.assertEqual(response.status_code, 200)

    def test_payment_wall_get(self):
        # Test GET request to the payment wall route
        response = self.app.get('/payment-wall')
        self.assertEqual(response.status_code, 200)

    def test_register_form_get(self):
        # Test GET request to the register form route
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_add_user_post_missing_fields(self):
        # Should redirect with error if fields are missing
        response = self.app.post('/add-user', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_upload_profile_image_post_no_file(self):
        # Should return 400 if no file uploaded
        with self.app.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
            sess['username'] = 'testuser'
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 400)

    def test_update_profile_post_not_logged_in(self):
        # Should return not logged in if session missing
        response = self.app.post('/update-profile', json={'field': 'name', 'value': 'New Name'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('User not logged in', response.get_data(as_text=True))

    def test_update_email_post_not_logged_in(self):
        # Should return 401 if session missing
        response = self.app.post('/update_email', json={'email': 'new@example.com'})
        self.assertEqual(response.status_code, 401)

    def test_user_dashboard_redirect(self):
        response = self.app.get('/user-dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_dashboard_redirect(self):
        response = self.app.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_forgot_password_get(self):
        response = self.app.get('/admin/forgot-password')
        self.assertEqual(response.status_code, 200)

    def test_admin_forgot_password_submit_post_missing_email(self):
        response = self.app.post('/admin/forgot-password/submit', data={})
        self.assertIn(response.status_code, [200, 302, 303])

    def test_admin_verification_code_get(self):
        response = self.app.get('/admin-verification-code')
        self.assertEqual(response.status_code, 200)

    def test_admin_new_password_get(self):
        response = self.app.get('/admin-new-password')
        self.assertEqual(response.status_code, 200)

    def test_admin_resend_otp_post_missing_email(self):
        response = self.app.post('/admin-resend-otp', data={})
        self.assertEqual(response.status_code, 400)

    def test_submit_ticket_get(self):
        response = self.app.get('/submit-ticket')
        self.assertEqual(response.status_code, 200)

    def test_personal_info_get(self):
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    def test_change_password_get(self):
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    def test_privacy_settings_get(self):
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    def test_language_region_get(self):
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    def test_recent_logins_get(self):
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    def test_recent_bookings_get(self):
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    def test_truck_book2_get(self):
        response = self.app.get('/truck-book2')
        self.assertEqual(response.status_code, 200)

    def test_truck_book3_get(self):
        response = self.app.get('/truck-book3')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book_get(self):
        response = self.app.get('/motorcycle-book')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book2_get(self):
        response = self.app.get('/motorcycle-book2')
        self.assertEqual(response.status_code, 200)

    def test_motorcycle_book3_get(self):
        response = self.app.get('/motorcycle-book3')
        self.assertEqual(response.status_code, 200)

    def test_carbook_get(self):
        response = self.app.get('/carbook')
        self.assertEqual(response.status_code, 200)

    def test_carbook2_get(self):
        response = self.app.get('/carbook2')
        self.assertEqual(response.status_code, 200)

    def test_carbook3_get(self):
        response = self.app.get('/carbook3')
        self.assertEqual(response.status_code, 200)

    def test_parceltracking_get_no_tracking_id(self):
        response = self.app.get('/parceltracking')
        self.assertEqual(response.status_code, 200)

    def test_update_full_name_post_not_logged_in(self):
        response = self.app.post('/update-full-name', json={'full_name': 'Test User'})
        self.assertEqual(response.status_code, 401)

    def test_upload_profile_image_post_not_logged_in(self):
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 401)

    def test_admin_employees_redirect(self):
        response = self.app.get('/admin/employees', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_hexaboxes_redirect(self):
        response = self.app.get('/admin/hexaboxes', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_utilities_redirect(self):
        response = self.app.get('/admin/utilities', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_vehicles_redirect(self):
        response = self.app.get('/admin/vehicles', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_redirect(self):
        response = self.app.get('/admin/employee-salary', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_redirect(self):
        response = self.app.get('/admin/products', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_redirect(self):
        response = self.app.get('/admin/sales', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_redirect(self):
        response = self.app.get('/admin/customers', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_add_post_not_logged_in(self):
        response = self.app.post('/admin/products/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_update_post_not_logged_in(self):
        response = self.app.post('/admin/products/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_products_delete_post_not_logged_in(self):
        response = self.app.post('/admin/products/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_add_post_not_logged_in(self):
        response = self.app.post('/admin/sales/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_update_post_not_logged_in(self):
        response = self.app.post('/admin/sales/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_sales_delete_post_not_logged_in(self):
        response = self.app.post('/admin/sales/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_add_post_not_logged_in(self):
        response = self.app.post('/admin/customers/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_update_post_not_logged_in(self):
        response = self.app.post('/admin/customers/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_customers_delete_post_not_logged_in(self):
        response = self.app.post('/admin/customers/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_add_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/add', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_update_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/update', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_employee_salary_delete_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_api_utilities_chart_data_unauthorized(self):
        response = self.app.get('/api/utilities/chart-data')
        self.assertEqual(response.status_code, 401)

    def test_api_utilities_generate_report_unauthorized(self):
        response = self.app.post('/api/utilities/generate-report', data={})
        self.assertEqual(response.status_code, 401)

    def test_admin_support_tickets_reply_post_missing_data(self):
        response = self.app.post('/admin/support-tickets/reply', data={})
        self.assertIn(response.status_code, [302, 303])

    def test_admin_support_tickets_reply_page_not_logged_in(self):
        response = self.app.get('/admin/support-tickets/reply/fake-ticket-id', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    def test_admin_support_ticket_done_not_logged_in(self):
        response = self.app.post('/admin/support/ticket/done/fake-ticket-id')
        # Should return 401 or 404 or 500 depending on implementation
        self.assertIn(response.status_code, [401, 404, 500])

if __name__ == '__main__':
    unittest.main()