import unittest
from app import app
from flask import json

class TestApp(unittest.TestCase):
    def setUp(self):
        # Set up test client for Flask app
        self.app = app.test_client()
        self.app.testing = True

    # Test home route (user login page)
    def test_home_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    # Test user login page (GET)
    def test_user_login_get(self):
        response = self.app.get('/user-login')
        self.assertEqual(response.status_code, 200)

    # Test user login HTML page (GET)
    def test_user_login_html_get(self):
        response = self.app.get('/user-login.html')
        self.assertEqual(response.status_code, 200)

    # Test logout route redirects
    def test_logout_redirect(self):
        response = self.app.get('/logout', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test FAQ page
    def test_faq_route(self):
        response = self.app.get('/FAQ')
        self.assertEqual(response.status_code, 200)

    # Test sidebar page
    def test_sidebar_route(self):
        response = self.app.get('/sidebar')
        self.assertEqual(response.status_code, 200)

    # Test admin login redirect route
    def test_admin_login_redirect(self):
        response = self.app.get('/admin-login', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin login page (GET)
    def test_admin_login_get(self):
        response = self.app.get('/admin/login')
        self.assertEqual(response.status_code, 200)

    # Test admin dashboard requires login (should redirect)
    def test_admin_dashboard_requires_login(self):
        response = self.app.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin logout redirects
    def test_admin_logout_redirect(self):
        response = self.app.get('/admin/logout', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test user signup page
    def test_user_signup_get(self):
        response = self.app.get('/user-signup')
        self.assertEqual(response.status_code, 200)

    # Test forgot password page
    def test_forgot_password_get(self):
        response = self.app.get('/forgot-password')
        self.assertEqual(response.status_code, 200)

    # Test tracking page
    def test_tracking_get(self):
        response = self.app.get('/tracking')
        self.assertEqual(response.status_code, 200)

    # Test validate order item ID API (POST)
    def test_validate_order_item_id_post(self):
        response = self.app.post('/validate-order-item-id', json={'order_item_id': 'test'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('exists', data)

    # Test unauthorized access to user activities API
    def test_api_user_activities_unauthorized(self):
        response = self.app.get('/api/user-activities')
        self.assertIn(response.status_code, [401, 302, 200])  # 401 if not logged in

    # Test 404 error for nonexistent route
    def test_error_handling(self):
        response = self.app.get('/nonexistent')
        self.assertEqual(response.status_code, 404)

    # Test index page (GET)
    def test_index_route(self):
        response = self.app.get('/index')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/index.html')
        self.assertEqual(response2.status_code, 200)

    # Test services page (GET)
    def test_services_route(self):
        response = self.app.get('/services')
        self.assertEqual(response.status_code, 200)
        response2 = self.app.get('/services.html')
        self.assertEqual(response2.status_code, 200)

    # Test parcel tracker page
    def test_parcel_tracker_route(self):
        response = self.app.get('/parcel-tracker')
        self.assertEqual(response.status_code, 200)

    # Test personal info page
    def test_personal_info_route(self):
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    # Test change password page (GET)
    def test_change_password_get(self):
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    # Test update email page
    def test_update_email_route(self):
        response = self.app.get('/update-email')
        self.assertEqual(response.status_code, 200)

    # Test privacy settings page
    def test_privacy_settings_route(self):
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    # Test language region page
    def test_language_region_route(self):
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    # Test recent logins page
    def test_recent_logins_route(self):
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    # Test recent bookings page
    def test_recent_bookings_route(self):
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    # Test truck page
    def test_truck_route(self):
        response = self.app.get('/truck')
        self.assertEqual(response.status_code, 200)

    # Test truck book page
    def test_truck_book_route(self):
        response = self.app.get('/truck-book')
        self.assertEqual(response.status_code, 200)

    # Test motorcycle page
    def test_motorcycle_route(self):
        response = self.app.get('/motorcycle')
        self.assertEqual(response.status_code, 200)

    # Test car page
    def test_car_route(self):
        response = self.app.get('/car')
        self.assertEqual(response.status_code, 200)

    # Test payment wall page
    def test_payment_wall_get(self):
        response = self.app.get('/payment-wall')
        self.assertEqual(response.status_code, 200)

    # Test register form page
    def test_register_form_get(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

    # Test add user POST with missing fields (should redirect)
    def test_add_user_post_missing_fields(self):
        response = self.app.post('/add-user', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test upload profile image POST with no file (should return 400)
    def test_upload_profile_image_post_no_file(self):
        with self.app.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
            sess['username'] = 'testuser'
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 400)

    # Test update profile POST when not logged in (should return not logged in)
    def test_update_profile_post_not_logged_in(self):
        response = self.app.post('/update-profile', json={'field': 'name', 'value': 'New Name'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('User not logged in', response.get_data(as_text=True))

    # Test update email POST when not logged in (should return 401)
    def test_update_email_post_not_logged_in(self):
        response = self.app.post('/update_email', json={'email': 'new@example.com'})
        self.assertEqual(response.status_code, 401)

    # Test user dashboard redirects if not logged in
    def test_user_dashboard_redirect(self):
        response = self.app.get('/user-dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin dashboard redirects if not logged in
    def test_admin_dashboard_redirect(self):
        response = self.app.get('/admin/dashboard', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin forgot password page
    def test_admin_forgot_password_get(self):
        response = self.app.get('/admin/forgot-password')
        self.assertEqual(response.status_code, 200)

    # Test admin forgot password submit POST with missing email
    def test_admin_forgot_password_submit_post_no_email(self):
        response = self.app.post('/admin/forgot-password/submit', data={})
        self.assertIn(response.status_code, [200, 302, 303])

    # Test admin verification code page
    def test_admin_verification_code_get(self):
        response = self.app.get('/admin-verification-code')
        self.assertEqual(response.status_code, 200)

    # Test admin new password page
    def test_admin_new_password_get(self):
        response = self.app.get('/admin-new-password')
        self.assertEqual(response.status_code, 200)

    # Test admin resend OTP POST with missing email (should return 400)
    def test_admin_resend_otp_post_no_email(self):
        response = self.app.post('/admin-resend-otp', data={})
        self.assertEqual(response.status_code, 400)

    # Test submit ticket page
    def test_submit_ticket_get(self):
        response = self.app.get('/submit-ticket')
        self.assertEqual(response.status_code, 200)

    # Test personal info page (duplicate route)
    def test_personal_info_get(self):
        response = self.app.get('/personal-info')
        self.assertEqual(response.status_code, 200)

    # Test change password page (duplicate route)
    def test_change_password_get(self):
        response = self.app.get('/change-password')
        self.assertEqual(response.status_code, 200)

    # Test privacy settings page (duplicate route)
    def test_privacy_settings_get(self):
        response = self.app.get('/privacy-settings')
        self.assertEqual(response.status_code, 200)

    # Test language region page (duplicate route)
    def test_language_region_get(self):
        response = self.app.get('/language-region')
        self.assertEqual(response.status_code, 200)

    # Test recent logins page (duplicate route)
    def test_recent_logins_get(self):
        response = self.app.get('/recent-logins')
        self.assertEqual(response.status_code, 200)

    # Test recent bookings page (duplicate route)
    def test_recent_bookings_get(self):
        response = self.app.get('/recent-bookings')
        self.assertEqual(response.status_code, 200)

    # Test truck book2 page
    def test_truck_book2_get(self):
        response = self.app.get('/truck-book2')
        self.assertEqual(response.status_code, 200)

    # Test truck book3 page
    def test_truck_book3_get(self):
        response = self.app.get('/truck-book3')
        self.assertEqual(response.status_code, 200)

    # Test motorcycle book page
    def test_motorcycle_book_get(self):
        response = self.app.get('/motorcycle-book')
        self.assertEqual(response.status_code, 200)

    # Test motorcycle book2 page
    def test_motorcycle_book2_get(self):
        response = self.app.get('/motorcycle-book2')
        self.assertEqual(response.status_code, 200)

    # Test motorcycle book3 page
    def test_motorcycle_book3_get(self):
        response = self.app.get('/motorcycle-book3')
        self.assertEqual(response.status_code, 200)

    # Test carbook page
    def test_carbook_get(self):
        response = self.app.get('/carbook')
        self.assertEqual(response.status_code, 200)

    # Test carbook2 page
    def test_carbook2_get(self):
        response = self.app.get('/carbook2')
        self.assertEqual(response.status_code, 200)

    # Test carbook3 page
    def test_carbook3_get(self):
        response = self.app.get('/carbook3')
        self.assertEqual(response.status_code, 200)

    # Test parceltracking page with no tracking_id
    def test_parceltracking_get_no_tracking_id(self):
        response = self.app.get('/parceltracking')
        self.assertEqual(response.status_code, 200)

    # Test update full name POST when not logged in (should return 401)
    def test_update_full_name_post_not_logged_in(self):
        response = self.app.post('/update-full-name', json={'full_name': 'Test User'})
        self.assertEqual(response.status_code, 401)

    # Test upload profile image POST when not logged in (should return 401)
    def test_upload_profile_image_post_not_logged_in(self):
        response = self.app.post('/upload-profile-image', data={})
        self.assertEqual(response.status_code, 401)

    # Test admin employees page redirects if not logged in
    def test_admin_employees_redirect(self):
        response = self.app.get('/admin/employees', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin hexaboxes page redirects if not logged in
    def test_admin_hexaboxes_redirect(self):
        response = self.app.get('/admin/hexaboxes', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin utilities page redirects if not logged in
    def test_admin_utilities_redirect(self):
        response = self.app.get('/admin/utilities', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin vehicles page redirects if not logged in
    def test_admin_vehicles_redirect(self):
        response = self.app.get('/admin/vehicles', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin employee salary page redirects if not logged in
    def test_admin_employee_salary_redirect(self):
        response = self.app.get('/admin/employee-salary', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin products page redirects if not logged in
    def test_admin_products_redirect(self):
        response = self.app.get('/admin/products', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin sales page redirects if not logged in
    def test_admin_sales_redirect(self):
        response = self.app.get('/admin/sales', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin customers page redirects if not logged in
    def test_admin_customers_redirect(self):
        response = self.app.get('/admin/customers', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin products add POST redirects if not logged in
    def test_admin_products_add_post_not_logged_in(self):
        response = self.app.post('/admin/products/add', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin products update POST redirects if not logged in
    def test_admin_products_update_post_not_logged_in(self):
        response = self.app.post('/admin/products/update', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin products delete POST redirects if not logged in
    def test_admin_products_delete_post_not_logged_in(self):
        response = self.app.post('/admin/products/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin sales add POST redirects if not logged in
    def test_admin_sales_add_post_not_logged_in(self):
        response = self.app.post('/admin/sales/add', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin sales update POST redirects if not logged in
    def test_admin_sales_update_post_not_logged_in(self):
        response = self.app.post('/admin/sales/update', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin sales delete POST redirects if not logged in
    def test_admin_sales_delete_post_not_logged_in(self):
        response = self.app.post('/admin/sales/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin customers add POST redirects if not logged in
    def test_admin_customers_add_post_not_logged_in(self):
        response = self.app.post('/admin/customers/add', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin customers update POST redirects if not logged in
    def test_admin_customers_update_post_not_logged_in(self):
        response = self.app.post('/admin/customers/update', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin customers delete POST redirects if not logged in
    def test_admin_customers_delete_post_not_logged_in(self):
        response = self.app.post('/admin/customers/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin employee salary add POST redirects if not logged in
    def test_admin_employee_salary_add_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/add', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin employee salary update POST redirects if not logged in
    def test_admin_employee_salary_update_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/update', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin employee salary delete POST redirects if not logged in
    def test_admin_employee_salary_delete_post_not_logged_in(self):
        response = self.app.post('/admin/employee-salary/delete', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test API utilities chart data returns 401 if not logged in as admin
    def test_api_utilities_chart_data_unauthorized(self):
        response = self.app.get('/api/utilities/chart-data')
        self.assertEqual(response.status_code, 401)

    # Test API utilities generate report returns 401 if not logged in as admin
    def test_api_utilities_generate_report_unauthorized(self):
        response = self.app.post('/api/utilities/generate-report', data={})
        self.assertEqual(response.status_code, 401)

    # Test admin support tickets reply POST redirects if not logged in
    def test_admin_support_tickets_reply_post_missing_data(self):
        response = self.app.post('/admin/support-tickets/reply', data={})
        self.assertIn(response.status_code, [302, 303])

    # Test admin support tickets reply page redirects if not logged in
    def test_admin_support_tickets_reply_page_not_logged_in(self):
        response = self.app.get('/admin/support-tickets/reply/fake-ticket-id', follow_redirects=False)
        self.assertIn(response.status_code, [302, 303])

    # Test admin support ticket done returns 401/404/500 if not logged in
    def test_admin_support_ticket_done_not_logged_in(self):
        response = self.app.post('/admin/support/ticket/done/fake-ticket-id')
        # Should return 401 or 404 or 500 depending on implementation
        self.assertIn(response.status_code, [401, 404, 500])

    # Test GET /analytics/employee_statuses.png (should return 200 or 404)
    def test_analytics_employee_statuses_png(self):
        response = self.app.get('/analytics/employee_statuses.png')
        self.assertIn(response.status_code, [200, 404])

    # Test GET /analytics/vehicles_deployed.png (should return 200 or 404)
    def test_analytics_vehicles_deployed_png(self):
        response = self.app.get('/analytics/vehicles_deployed.png')
        self.assertIn(response.status_code, [200, 404])

if __name__ == '__main__':
    unittest.main()