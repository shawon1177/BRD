from rest_framework_simplejwt.tokens import RefreshToken



class JWTHandler:

    
    def Make_user_jwt(self,user):
        try:
            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token
            return refresh_token, access_token
        except Exception as e:
           print("Error creating JWT for user")
    
           return None,None



UserTokenGeneration = JWTHandler()