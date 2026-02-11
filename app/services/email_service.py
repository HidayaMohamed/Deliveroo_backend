"""
Email Notification Service
Sends emails for order status updates and notifications
"""
from flask_mail import Message
from app import mail


class EmailService:
    
    @staticmethod
    def send_status_email(user_email, user_name, order_id, status, courier_name=None, courier_phone=None):
        """
        Send email when order status is updated.
        Used for status updates like 'Courier Assigned' and 'Delivered'.
        
        Args:
            user_email (str): Customer's email address
            user_name (str): Customer's name
            order_id (int): Order ID
            status (str): New order status (e.g., 'Courier Assigned', 'Delivered')
            courier_name (str, optional): Courier's name for 'Courier Assigned' status
            courier_phone (str, optional): Courier's phone for 'Courier Assigned' status
            
        Returns:
            dict: Status with message
        """
        try:
            # Create professional subject line
            status_messages = {
                'Courier Assigned': 'Courier Assigned to Your Order',
                'Delivered': 'Your Order Has Been Delivered!',
                'Picked Up': 'Your Order Has Been Picked Up',
                'In Transit': 'Your Order Is On Its Way',
                'Pending': 'Order Received - Pending Assignment',
                'Cancelled': 'Order Has Been Cancelled'
            }
            
            subject_prefix = status_messages.get(status, f'Order #{order_id} Update')
            
            # Create professional email content
            msg = Message(
                subject=f'Deliveroo - {subject_prefix}',
                recipients=[user_email]
            )
            
            # Dynamic content based on status
            status_content = {
                'Courier Assigned': f"""
🚚 Great news, {user_name}! A courier has been assigned to your order.

Your package is now being handled by our delivery team.
                """,
                'Delivered': f"""
✅ Success! Your order #{order_id} has been delivered.

Thank you for using Deliveroo. We hope you enjoy your delivery!

Please rate your delivery experience.
                """,
                'Picked Up': f"""
📦 Your order #{order_id} has been picked up by the courier.

It's now on its way to you!
                """,
                'In Transit': f"""
🚗 Your order #{order_id} is on its way!

The courier is currently en route to the delivery location.
                """,
                'Pending': f"""
📋 Order #{order_id} has been received and is pending assignment.

A courier will be assigned shortly.
                """,
                'Cancelled': f"""
❌ Order #{order_id} has been cancelled.

If you have any questions, please contact our support team.
                """
            }
            
            content = status_content.get(status, f'Your order status has been updated to: {status}')
            
            # Add courier details if available
            courier_details = ""
            if status == 'Courier Assigned' and courier_name:
                courier_details = f"""
👤 Courier Details:
   Name: {courier_name}
   Phone: {courier_phone or 'N/A'}
"""
            
            msg.body = f"""
Hello {user_name},

{content}
{courier_details}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Order Details
Order ID: #{order_id}
Current Status: {status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Track your order: https://deliveroo.com/track/{order_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Thank you for choosing Deliveroo!

Best regards,
The Deliveroo Team

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📧 This is an automated message. Please do not reply directly to this email.
            """
            
            mail.send(msg)
            return {{
                'status': 'success', 
                'message': f'Email sent successfully for status: {status}',
                'order_id': order_id,
                'recipient': user_email
            }}
            
        except Exception as e:
            return {{
                'status': 'error', 
                'message': f'Failed to send status email: {{str(e)}}',
                'error_type': type(e).__name__
            }}
    
    
    @staticmethod
    def send_courier_assigned(user_email, order_id, courier_name, courier_phone):
        """
        Send email when courier is assigned
        
        Args:
            user_email (str): Customer's email
            order_id (int): Order ID
            courier_name (str): Courier's name
            courier_phone (str): Courier's phone number
        """
        try:
            msg = Message(
                subject=f'Deliveroo - Courier Assigned to Order #{order_id}',
                recipients=[user_email]
            )
            
            msg.body = f"""
Hello,

Great news! A courier has been assigned to your order #{order_id}.

Courier Details:
Name: {courier_name}
Phone: {courier_phone}

You will receive updates as your parcel moves through the delivery process.

Track your order at: https://deliveroo.com/track/{order_id}

Thank you for using Deliveroo!

Best regards,
Deliveroo Team
            """
            
            mail.send(msg)
            return {'status': 'success', 'message': 'Email sent'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    
    @staticmethod
    def send_delivery_complete(user_email, order_id):
        """
        Send email when delivery is completed
        
        Args:
            user_email (str): Customer's email
            order_id (int): Order ID
        """
        try:
            msg = Message(
                subject=f'Deliveroo - Order #{order_id} Delivered!',
                recipients=[user_email]
            )
            
            msg.body = f"""
Hello,

Your order #{order_id} has been successfully delivered!

We hope you're satisfied with our service.

Please rate your delivery experience: https://deliveroo.com/rate/{order_id}

Thank you for using Deliveroo!

Best regards,
Deliveroo Team
            """
            
            mail.send(msg)
            return {'status': 'success', 'message': 'Email sent'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}