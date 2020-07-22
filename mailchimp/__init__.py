from .mailchimp import Mailchimp

def setup(bot):
    bot.add_cog(Mailchimp(bot))
