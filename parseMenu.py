from square.client import Client


client = Client(
  access_token="EAAAEK8AT3RsMSSRPHMCED2XtgDiOG3y0BnWtIgjNSp8mS6Rmt50iomrWAOMIk6Z",
  environment="sandbox"
)



def get_menuAPI():
    result = client.catalog.list_catalog(
        types = "ITEM"
    )

    if result.is_success():
        print(result.body)
    elif result.is_error():
        print(result.errors)

    return str(result.body)



