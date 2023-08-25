##### Share notes
To share a layer between accounts or even publish it publicly, you need to use the AWS CLI or the API, as this is not supported in the console yet. We add permission statements using the AddLayerVersionPermission API action, which is similar to the way we do it with Lambda functions.

```bash
aws lambda add-layer-version-permission    --layer-name REPLACE_LAYER_NAME    --version-number 1    --statement-id sharingWithOneAccount    --principal REPLACE_ACCOUNT_ID    --action lambda:GetLayerVersion
```

You can replace REPLACE_LAYER_NAME&REPLACE_ACCOUNT_ID for your own parameters.

##### Used the shared version in another account
You can add the shared layer arn to use the layer, but it will not display in the Layer items.