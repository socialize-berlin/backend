from graphene_django import DjangoObjectType
import graphene
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from graphql_jwt.decorators import login_required
from api.models import Message as MessageModel, Connection as ConnectionModel, ConnectionMessage as ConnectionMessageModel, PasswordReset as PasswordResetModel
import graphql_jwt
from graphql_jwt.shortcuts import get_token
from django.db.models import Q
from api.helpers.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime, timedelta

UserModel = get_user_model()


class User(DjangoObjectType):
    pending_connections_count = graphene.NonNull(graphene.Int)
    unread_messages_count = graphene.NonNull(graphene.Int)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'headline', 'introduction', 'avatar', 'lat', 'lng']

    def resolve_pending_connections_count(self, info):
        if self.id != info.context.user.id:
            return 0

        return ConnectionModel.objects.filter(invitee=info.context.user, status="P").count()

    def resolve_unread_messages_count(self, info):
        if self.id != info.context.user.id:
            return 0

        return ConnectionMessageModel.objects.filter(Q(connection__author=info.context.user) | Q(connection__invitee=info.context.user), connection__status='A', is_seen=False).exclude(author=info.context.user).count()



class Message(DjangoObjectType):
    class Meta:
        model = MessageModel
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'headline', 'introduction', 'avatar', 'lat', 'lng']

class ConversationMessage(DjangoObjectType):
    author = graphene.Field(graphene.NonNull(User))

    class Meta:
        model = ConnectionMessageModel
        fields = ['id', 'author', 'message', 'is_seen', 'created']

class Conversation(DjangoObjectType):
    invitee = graphene.Field(graphene.NonNull(User))
    author = graphene.Field(graphene.NonNull(User))
    messages = graphene.List(graphene.NonNull(ConversationMessage))
    last_message = graphene.Field(ConversationMessage)
    is_seen = graphene.Boolean()

    class Meta:
        model = ConnectionModel
        fields = ['uuid', 'author', 'invitee', 'messages', 'last_message', 'created']


    def resolve_last_message(self, info):
        return ConnectionMessageModel.objects.filter(connection=self).order_by('-created').first()

    def resolve_messages(self, info):
        return ConnectionMessageModel.objects.filter(connection=self).order_by('-created')

    def resolve_is_seen(self, info):
        opponent = self.invitee if self.invitee.id != info.context.user.id else self.author

        return not ConnectionMessageModel.objects.filter(connection=self, author=opponent, is_seen=False).exists()

class Connection(DjangoObjectType):
    invitee = graphene.Field(graphene.NonNull(User))
    author = graphene.Field(graphene.NonNull(User))

    class Meta:
        model = ConnectionModel
        fields = ['uuid', 'author', 'invitee', 'message', 'status', 'created']


class CreateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=False)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(lambda: User)
    token = graphene.String()

    def mutate(root, info, first_name, last_name, email, password):
        try:
            username = slugify(email)
            user = UserModel.objects.create(
                username=username, 
                first_name=first_name, 
                last_name=last_name, 
                email=email,
            )

            user.set_password(password)
            user.save()
        except:
            raise Exception('Error creating user')

        token = get_token(user)

        return CreateUser(user=user, token=token)


class ResetPassword(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, email):
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise Exception('User with this email does not exist')

        try:
            password_reset = PasswordResetModel.objects.create(user=user)
            reset_link = f"https://socialize.berlin/reset-password/{password_reset.token}"
            context = {
                'title': 'Reset Password',
                'reset_link': reset_link
            }

            html_content = render_to_string(
                'api/reset_password.html', context)

            send_mail(
                to_emails=password_reset.user.email,
                subject='Reset your account password',
                html_content=html_content
            )

        except:
            raise Exception('Error resetting password')


        return ResetPassword(ok=True)

class SetPassword(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        password = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, token, password):
        yesterday = datetime.now() - timedelta(days=1)

        try:
            reset_password = PasswordResetModel.objects.get(
                token=token, used=False, created__gt=yesterday)
        except PasswordResetModel.DoesNotExist:
            raise Exception('Reset password token is expired')

        try:
            reset_password.user.set_password(password)
            reset_password.user.save()
            reset_password.used = True
            reset_password.save()

        except:
            raise Exception('Error setting new password')


        return SetPassword(ok=True)

class SendMessage(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        message = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, name, message, email):
        try:
            message = MessageModel.objects.create(name=name, email=email, message=message)
        except:
            raise Exception('Error sending message')

        return SendMessage(ok=True)

class UnlistUser(graphene.Mutation):
    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @login_required
    def mutate(root, info):
        try:
            user = UserModel.objects.get(pk=info.context.user.id)
            user.lat = None
            user.lng = None
            user.save()
        except:
            raise Exception('Error updating location')

        return UnlistUser(ok=True, user=user)

class UpdateUser(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=False)
        headline = graphene.String(required=False)
        introduction = graphene.String(required=False)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @login_required
    def mutate(root, info, first_name, last_name, headline, introduction):
        try:
            user = UserModel.objects.get(pk=info.context.user.id)
            user.first_name = first_name
            user.last_name = last_name
            user.headline = headline
            user.introduction = introduction
            user.save()
        except:
            raise Exception('Error updating user')

        return UpdateUser(ok=True, user=user)

class DeleteUser(graphene.Mutation):
    ok = graphene.Boolean()

    @login_required
    def mutate(root, info):
        try:
            user = UserModel.objects.get(pk=info.context.user.id)
            user.delete()
        except:
            raise Exception('Error deleting user')

        return DeleteUser(ok=True)


class SendConnectionInvite(graphene.Mutation):
    class Arguments:
        invitee_id = graphene.ID(required=True)
        message = graphene.String(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, invitee_id, message):
        try:
            invitee = UserModel.objects.get(pk=invitee_id)
        except UserModel.DoesNotExist:
            raise Exception('Error finding user')

        existing_connection = ConnectionModel.objects.filter(author=info.context.user, invitee=invitee).first()

        if existing_connection:
            if existing_connection.status == 'P':
                raise Exception('Connection request already sent')
            elif existing_connection.status == 'A':
                raise Exception('User is already connected with you')
            elif existing_connection.status == 'R':
                raise Exception('User has rejected your connection request')

        try:
            connection = ConnectionModel.objects.create(author=info.context.user, invitee=invitee, message=message)
        except:
            raise Exception('Error sending connection invite')

        return SendConnectionInvite(ok=True)

class CancelConnectionInvite(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id):
        try:
            connection = ConnectionModel.objects.get(pk=connection_id, author=info.context.user)
        except ConnectionModel.DoesNotExist:
            raise Exception('Error canceling connection request')

        connection.delete()

        return CancelConnectionInvite(ok=True)

class AcceptConnectionInvite(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id):
        try:
            connection = ConnectionModel.objects.get(pk=connection_id, invitee=info.context.user)
        except ConnectionModel.DoesNotExist:
            raise Exception('Error accepting connection request')

        connection.status = 'A'
        connection.save()

        return AcceptConnectionInvite(ok=True)

class DeclineConnectionInvite(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id):
        try:
            connection = ConnectionModel.objects.get(pk=connection_id, invitee=info.context.user)
        except ConnectionModel.DoesNotExist:
            raise Exception('Error declining connection request')

        connection.status = 'R'
        connection.save()

        return DeclineConnectionInvite(ok=True)

class RemoveConnection(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id):
        try:
            connection = ConnectionModel.objects.get(Q(author=info.context.user) | Q(invitee=info.context.user), pk=connection_id)
        except ConnectionModel.DoesNotExist:
            raise Exception('Error removing connection')

        connection.delete()

        return RemoveConnection(ok=True)

class SendConversationMessage(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)
        message = graphene.String(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id, message):
        try:
            connection = ConnectionModel.objects.get(Q(author=info.context.user) | Q(invitee=info.context.user), pk=connection_id, status='A')
        except ConnectionModel.DoesNotExist:
            raise Exception('Conversation not found')

        opponent = connection.author if connection.invitee == info.context.user else connection.invitee

        ConnectionMessageModel.objects.create(connection=connection, author=info.context.user, message=message)
        ConnectionMessageModel.objects.filter(connection=connection, author=opponent).update(is_seen=True)

        return SendConversationMessage(ok=True)

class ReadAllMessages(graphene.Mutation):
    class Arguments:
        connection_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @login_required
    def mutate(root, info, connection_id):
        try:
            connection = ConnectionModel.objects.get(Q(author=info.context.user) | Q(invitee=info.context.user), pk=connection_id, status='A')
        except ConnectionModel.DoesNotExist:
            raise Exception('Conversation not found')

        opponent = connection.author if connection.invitee == info.context.user else connection.invitee

        ConnectionMessageModel.objects.filter(connection=connection, author=opponent).update(is_seen=True)

        return ReadAllMessages(ok=True)


class PlaceOnMap(graphene.Mutation):
    class Arguments:
        lat = graphene.Decimal(required=True)
        lng = graphene.Decimal(required=True)
        headline = graphene.String(required=True)
        introduction = graphene.String(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @login_required
    def mutate(root, info, lat, lng, headline, introduction):
        try:
            user = UserModel.objects.get(pk=info.context.user.id)
            user.headline = headline
            user.introduction = introduction
            user.lat = lat
            user.lng = lng
            user.save()
        except:
            raise Exception('Error placing on map')

        return PlaceOnMap(ok=True, user=user)



class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()
    reset_password = ResetPassword.Field()
    set_password = SetPassword.Field()
    placeOnMap = PlaceOnMap.Field()
    updateUser = UpdateUser.Field()
    unlistUser = UnlistUser.Field()
    deleteUser = DeleteUser.Field()
    readAllMessages = ReadAllMessages.Field()
    removeConnection = RemoveConnection.Field()
    acceptConnectionInvite = AcceptConnectionInvite.Field()
    declineConnectionInvite = DeclineConnectionInvite.Field()
    cancelConnectionInvite = CancelConnectionInvite.Field()
    sendConnectionInvite = SendConnectionInvite.Field()
    sendConversationMessage = SendConversationMessage.Field()
    send_message = SendMessage.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()    

class Query(graphene.ObjectType):
    users = graphene.List(graphene.NonNull(User))
    me = graphene.Field(User)
    connections = graphene.List(graphene.NonNull(Connection))
    conversations = graphene.List(graphene.NonNull(Conversation))
    conversation = graphene.Field(graphene.NonNull(Conversation), uuid=graphene.ID())

    @login_required
    def resolve_users(self, info):
        return UserModel.objects.filter(lat__isnull=False, lng__isnull=False).order_by('-id')

    @login_required
    def resolve_connections(self, info):
        return ConnectionModel.objects.filter(Q(author=info.context.user) | Q(invitee=info.context.user)).order_by('-created')

    @login_required
    def resolve_conversations(self, info):
        return ConnectionModel.objects.filter(Q(author=info.context.user) | Q(invitee=info.context.user), status="A").order_by('-created')

    @login_required
    def resolve_conversation(self, info, uuid):
        return ConnectionModel.objects.get(Q(author=info.context.user) | Q(invitee=info.context.user), status="A", pk=uuid)

    @login_required
    def resolve_me(self, info):
        return UserModel.objects.get(pk=info.context.user.id)

schema = graphene.Schema(query=Query, mutation=Mutations)