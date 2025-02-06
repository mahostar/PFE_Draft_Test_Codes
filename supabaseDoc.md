Documentation for the project (supabase) :

Storage
Uploads
S3 Uploads
S3 Uploads
Learn how to upload files to Supabase Storage using S3.
You can use the S3 protocol to upload files to Supabase Storage. To get started with S3, see the S3 setup guide.

The S3 protocol supports file upload using:

A single request
Multiple requests via Multipart Upload
Single request uploads#
The PutObject action uploads the file in a single request. This matches the behavior of the Supabase SDK Standard Upload.

Use PutObject to upload smaller files, where retrying the entire upload won't be an issue. The maximum file size on paid plans is 50 GB.

For example, using JavaScript and the aws-sdk client:

import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3'

const s3Client = new S3Client({...})

const file = fs.createReadStream('path/to/file')

const uploadCommand = new PutObjectCommand({
  Bucket: 'bucket-name',
  Key: 'path/to/file',
  Body: file,
  ContentType: 'image/jpeg',
})

await s3Client.send(uploadCommand)

Multipart uploads#
Multipart Uploads split the file into smaller parts and upload them in parallel, maximizing the upload speed on a fast network. When uploading large files, this allows you to retry the upload of individual parts in case of network issues.

This method is preferable over Resumable Upload for server-side uploads, when you want to maximize upload speed at the cost of resumability. The maximum file size on paid plans is 50 GB.

Upload a file in parts#
Use the Upload class from an S3 client to upload a file in parts. For example, using JavaScript:

import { S3Client } from '@aws-sdk/client-s3'
import { Upload } from '@aws-sdk/lib-storage'

const s3Client = new S3Client({...})

const file = fs.createReadStream('path/to/very-large-file')

const upload = new Upload(s3Client, {
  Bucket: 'bucket-name',
  Key: 'path/to/file',
  ContentType: 'image/jpeg',
  Body: file,
})

await uploader.done()

Aborting multipart uploads#
All multipart uploads are automatically aborted after 24 hours. To abort a multipart upload before that, you can use the AbortMultipartUpload action.

Edit this page on GitHub
Is this helpful?

Yes

No
On this page
Single request uploads
Multipart uploads
Upload a file in parts
Aborting multipart uploads
Need some help?

Contact support
Latest product updates?

See Changelog
Something's not right?

Check system status

------------------------------------------------

Storage
Uploads
Limits
Limits
Learn how to increase Supabase file limits.
Global file size#
You can set the max file size across all your buckets by setting this global value in the dashboard here. For Free projects, the limit can't exceed 50 MB. On the Pro Plan and up, you can set this value to up to 50 GB. If you need more than 50 GB, contact us.

Plan	Max File Size Limit
Free	50 MB
Pro	50 GB
Team	50 GB
Enterprise	Custom
This option is a global limit, which applies to all your buckets.

Additionally, you can specify the max file size on a per bucket level but it can't be higher than this global limit. As a good practice, the global limit should be set to the highest possible file size that your application accepts, and apply per bucket limits.

Per bucket restrictions#
You can have different restrictions on a per bucket level such as restricting the file types (e.g. pdf, images, videos) or the max file size, which should be lower than the global limit. To apply these limit on a bucket level see Creating Buckets.

------------------------------------------------

Storage
Uploads
Standard Uploads
Standard Uploads
Learn how to upload files to Supabase Storage.
Uploading#
The standard file upload method is ideal for small files that are not larger than 6MB.

It uses the traditional multipart/form-data format and is simple to implement using the supabase-js SDK. Here's an example of how to upload a file using the standard upload method:

Though you can upload up to 5GB files using the standard upload method, we recommend using TUS Resumable Upload for uploading files greater than 6MB in size for better reliability.


JavaScript

Dart

Swift

Kotlin

Python
response = supabase.storage.from_('bucket_name').upload('file_path', file)

Overwriting files#
When uploading a file to a path that already exists, the default behavior is to return a 400 Asset Already Exists error.
If you want to overwrite a file on a specific path you can set the upsert options to true or using the x-upsert header.


JavaScript

Dart

Swift

Kotlin

Python
response = supabase.storage.from_('bucket_name').upload('file_path', file, {
  'upsert': 'true',
})

We do advise against overwriting files when possible, as our Content Delivery Network will take sometime to propagate the changes to all the edge nodes leading to stale content.
Uploading a file to a new path is the recommended way to avoid propagation delays and stale content.

Content type#
By default, Storage will assume the content type of an asset from the file extension. If you want to specify the content type for your asset simply pass the contentType option during upload.


JavaScript

Dart

Swift

Kotlin

Python
response = supabase.storage.from_('bucket_name').upload('file_path', file, {
  'content-type': 'image/jpeg',
})

Concurrency#
When two or more clients upload a file to the same path, the first client to complete the upload will succeed and the other clients will receive a 400 Asset Already Exists error.
If you provide the x-upsert header the last client to complete the upload will succeed instead.

------------------------------------------------
S3 Authentication
Learn about authenticating with Supabase Storage S3.
You have two options to authenticate with Supabase Storage S3:

Using the generated S3 access keys from your project settings (Intended exclusively for server-side use)
Using a Session Token, which will allow you to authenticate with a user JWT token and provide limited access via Row Level Security (RLS).
S3 access keys#
Keep these credentials secure
S3 access keys provide full access to all S3 operations across all buckets and bypass RLS policies. These are meant to be used only on the server.

To authenticate with S3, generate a pair of credentials (Access Key ID and Secret Access Key), copy the endpoint and region from the project settings page.

This is all the information you need to connect to Supabase Storage using any S3-compatible service.

Storage S3 Access keys

aws-sdk-js

AWS Credentials
import { S3Client } from '@aws-sdk/client-s3';

const client = new S3Client({
  forcePathStyle: true,
  region: 'project_region',
  endpoint: 'https://project_ref.supabase.co/storage/v1/s3',
  credentials: {
    accessKeyId: 'your_access_key_id',
    secretAccessKey: 'your_secret_access_key',
  }
})

Session token#
You can authenticate to Supabase S3 with a user JWT token to provide limited access via RLS to all S3 operations. This is useful when you want initialize the S3 client on the server scoped to a specific user, or use the S3 client directly from the client side.

All S3 operations performed with the Session Token are scoped to the authenticated user. RLS policies on the Storage Schema are respected.

To authenticate with S3 using a Session Token, use the following credentials:

access_key_id: project_ref
secret_access_key: anonKey
session_token: valid jwt token
For example, using the aws-sdk library:

import { S3Client } from '@aws-sdk/client-s3'

const {
  data: { session },
} = await supabase.auth.getSession()

const client = new S3Client({
  forcePathStyle: true,
  region: 'project_region',
  endpoint: 'https://project_ref.supabase.co/storage/v1/s3',
  credentials: {
    accessKeyId: 'project_ref',
    secretAccessKey: 'anonKey',
    sessionToken: session.access_token,
  },
})

------------------------------------------------

S3 Compatibility
Learn about the compatibility of Supabase Storage with S3.
Supabase Storage is compatible with the S3 protocol. You can use any S3 client to interact with your Storage objects.

Storage supports standard, resumable and S3 uploads and all these protocols are interoperable. You can upload a file with the S3 protocol and list it with the REST API or upload with Resumable uploads and list with S3.

The S3 protocol is currently in Public Alpha. If you encounter any issues or have feature requests, contact us.

Implemented endpoints#
The most commonly used endpoints are implemented, and more will be added. Implemented S3 endpoints are marked with ✅ in the following tables.

Bucket operations#
API Name	Feature
✅ ListBuckets	
✅ HeadBucket	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ CreateBucket	❌ ACL:
❌ x-amz-acl
❌ x-amz-grant-full-control
❌ x-amz-grant-read
❌ x-amz-grant-read-acp
❌ x-amz-grant-write
❌ x-amz-grant-write-acp
❌ Object Locking:
❌ x-amz-bucket-object-lock-enabled
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ DeleteBucket	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ GetBucketLocation	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ DeleteBucketCors	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ GetBucketEncryption	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ GetBucketLifecycleConfiguration	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ GetBucketCors	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ PutBucketCors	❌ Checksums:
❌ x-amz-sdk-checksum-algorithm
❌ x-amz-checksum-algorithm
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ PutBucketLifecycleConfiguration	❌ Checksums:
❌ x-amz-sdk-checksum-algorithm
❌ x-amz-checksum-algorithm
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
Object operations#
API Name	Feature
✅ HeadObject	✅ Conditional Operations:
✅ If-Match
✅ If-Modified-Since
✅ If-None-Match
✅ If-Unmodified-Since
✅ Range:
✅ Range (has no effect in HeadObject)
✅ partNumber
❌ SSE-C:
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ ListObjects	Query Parameters:
✅ delimiter
✅ encoding-type
✅ marker
✅ max-keys
✅ prefix
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ ListObjectsV2	Query Parameters:
✅ list-type
✅ continuation-token
✅ delimiter
✅ encoding-type
✅ fetch-owner
✅ max-keys
✅ prefix
✅ start-after
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ GetObject	✅ Conditional Operations:
✅ If-Match
✅ If-Modified-Since
✅ If-None-Match
✅ If-Unmodified-Since
✅ Range:
✅ Range
✅ PartNumber
❌ SSE-C:
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ PutObject	System Metadata:
✅ Content-Type
✅ Cache-Control
✅ Content-Disposition
✅ Content-Encoding
✅ Content-Language
✅ Expires
❌ Content-MD5
❌ Object Lifecycle
❌ Website:
❌ x-amz-website-redirect-location
❌ SSE-C:
❌ x-amz-server-side-encryption
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ x-amz-server-side-encryption-aws-kms-key-id
❌ x-amz-server-side-encryption-context
❌ x-amz-server-side-encryption-bucket-key-enabled
❌ Request Payer:
❌ x-amz-request-payer
❌ Tagging:
❌ x-amz-tagging
❌ Object Locking:
❌ x-amz-object-lock-mode
❌ x-amz-object-lock-retain-until-date
❌ x-amz-object-lock-legal-hold
❌ ACL:
❌ x-amz-acl
❌ x-amz-grant-full-control
❌ x-amz-grant-read
❌ x-amz-grant-read-acp
❌ x-amz-grant-write-acp
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ DeleteObject	❌ Multi-factor authentication:
❌ x-amz-mfa
❌ Object Locking:
❌ x-amz-bypass-governance-retention
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ DeleteObjects	❌ Multi-factor authentication:
❌ x-amz-mfa
❌ Object Locking:
❌ x-amz-bypass-governance-retention
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ ListMultipartUploads	✅ Query Parameters:
✅ delimiter
✅ encoding-type
✅ key-marker
✅️ max-uploads
✅ prefix
✅ upload-id-marker
✅ CreateMultipartUpload	✅ System Metadata:
✅ Content-Type
✅ Cache-Control
✅ Content-Disposition
✅ Content-Encoding
✅ Content-Language
✅ Expires
❌ Content-MD5
❌ Website:
❌ x-amz-website-redirect-location
❌ SSE-C:
❌ x-amz-server-side-encryption
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ x-amz-server-side-encryption-aws-kms-key-id
❌ x-amz-server-side-encryption-context
❌ x-amz-server-side-encryption-bucket-key-enabled
❌ Request Payer:
❌ x-amz-request-payer
❌ Tagging:
❌ x-amz-tagging
❌ Object Locking:
❌ x-amz-object-lock-mode
❌ x-amz-object-lock-retain-until-date
❌ x-amz-object-lock-legal-hold
❌ ACL:
❌ x-amz-acl
❌ x-amz-grant-full-control
❌ x-amz-grant-read
❌ x-amz-grant-read-acp
❌ x-amz-grant-write-acp
❌ Storage class:
❌ x-amz-storage-class
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ CompleteMultipartUpload	❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ Request Payer:
❌ x-amz-request-payer
✅ AbortMultipartUpload	❌ Request Payer:
❌ x-amz-request-payer
✅ CopyObject	✅ Operation Metadata:
⚠️ x-amz-metadata-directive
✅ System Metadata:
✅ Content-Type
✅ Cache-Control
✅ Content-Disposition
✅ Content-Encoding
✅ Content-Language
✅ Expires
✅ Conditional Operations:
✅ x-amz-copy-source
✅ x-amz-copy-source-if-match
✅ x-amz-copy-source-if-modified-since
✅ x-amz-copy-source-if-none-match
✅ x-amz-copy-source-if-unmodified-since
❌ ACL:
❌ x-amz-acl
❌ x-amz-grant-full-control
❌ x-amz-grant-read
❌ x-amz-grant-read-acp
❌ x-amz-grant-write-acp
❌ Website:
❌ x-amz-website-redirect-location
❌ SSE-C:
❌ x-amz-server-side-encryption
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ x-amz-server-side-encryption-aws-kms-key-id
❌ x-amz-server-side-encryption-context
❌ x-amz-server-side-encryption-bucket-key-enabled
❌ x-amz-copy-source-server-side-encryption-customer-algorithm
❌ x-amz-copy-source-server-side-encryption-customer-key
❌ x-amz-copy-source-server-side-encryption-customer-key-MD5
❌ Request Payer:
❌ x-amz-request-payer
❌ Tagging:
❌ x-amz-tagging
❌ x-amz-tagging-directive
❌ Object Locking:
❌ x-amz-object-lock-mode
❌ x-amz-object-lock-retain-until-date
❌ x-amz-object-lock-legal-hold
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ x-amz-source-expected-bucket-owner
❌ Checksums:
❌ x-amz-checksum-algorithm
✅ UploadPart	✅ System Metadata:
❌ Content-MD5
❌ SSE-C:
❌ x-amz-server-side-encryption
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
✅ UploadPartCopy	❌ Conditional Operations:
❌ x-amz-copy-source
❌ x-amz-copy-source-if-match
❌ x-amz-copy-source-if-modified-since
❌ x-amz-copy-source-if-none-match
❌ x-amz-copy-source-if-unmodified-since
✅ Range:
✅ x-amz-copy-source-range
❌ SSE-C:
❌ x-amz-server-side-encryption-customer-algorithm
❌ x-amz-server-side-encryption-customer-key
❌ x-amz-server-side-encryption-customer-key-MD5
❌ x-amz-copy-source-server-side-encryption-customer-algorithm
❌ x-amz-copy-source-server-side-encryption-customer-key
❌ x-amz-copy-source-server-side-encryption-customer-key-MD5
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner
❌ x-amz-source-expected-bucket-owner
✅ ListParts	Query Parameters:
✅ max-parts
✅ part-number-marker
❌ Request Payer:
❌ x-amz-request-payer
❌ Bucket Owner:
❌ x-amz-expected-bucket-owner

------------------------------------------------

Storage
Use Supabase to store and serve files.
Supabase Storage makes it simple to upload and serve files of any size, providing a robust framework for file access controls.

Features#
You can use Supabase Storage to store images, videos, documents, and any other file type. Serve your assets with a global CDN to reduce latency from over 285 cities globally. Supabase Storage includes a built-in image optimizer, so you can resize and compress your media files on the fly.

Examples#
Check out all of the Storage templates and examples in our GitHub repository.

Resumable Uploads with Uppy
Resumable Uploads with Uppy

Use Uppy to upload files to Supabase Storage using the TUS protocol (resumable uploads).
Resources#
Find the source code and documentation in the Supabase GitHub repository.

Supabase Storage API

View the source code.
OpenAPI Spec

See the Swagger Documentation for Supabase Storage.

------------------------------------------------


Storage Quickstart
Learn how to use Supabase to store and serve files.
This guide shows the basic functionality of Supabase Storage. Find a full example application on GitHub.

Concepts#
Supabase Storage consists of Files, Folders, and Buckets.

Files#
Files can be any sort of media file. This includes images, GIFs, and videos. It is best practice to store files outside of your database because of their sizes. For security, HTML files are returned as plain text.

Folders#
Folders are a way to organize your files (just like on your computer). There is no right or wrong way to organize your files. You can store them in whichever folder structure suits your project.

Buckets#
Buckets are distinct containers for files and folders. You can think of them like "super folders". Generally you would create distinct buckets for different Security and Access Rules. For example, you might keep all video files in a "video" bucket, and profile pictures in an "avatar" bucket.

File, Folder, and Bucket names must follow AWS object key naming guidelines and avoid use of any other characters.

Create a bucket#
You can create a bucket using the Supabase Dashboard. Since the storage is interoperable with your Postgres database, you can also use SQL or our
client libraries. Here we create a bucket called "avatars":


Dashboard

SQL

JavaScript

Dart

Swift

Python
response = supabase.storage.create_bucket('avatars')

Reference.

Upload a file#
You can upload a file from the Dashboard, or within a browser using our JS libraries.


Dashboard

JavaScript

Dart
Go to the Storage page in the Dashboard.
Select the bucket you want to upload the file to.
Click Upload File.
Select the file you want to upload.
Download a file#
You can download a file from the Dashboard, or within a browser using our JS libraries.


Dashboard

JavaScript

Dart

Swift

Python
response = supabase.storage.from_('avatars').download('public/avatar1.png')

Reference.

Add security rules#
To restrict access to your files you can use either the Dashboard or SQL.


Dashboard

SQL
Go to the Storage page in the Dashboard.
Click Policies in the sidebar.
Click Add Policies in the OBJECTS table to add policies for Files. You can also create policies for Buckets.
Choose whether you want the policy to apply to downloads (SELECT), uploads (INSERT), updates (UPDATE), or deletes (DELETE).
Give your policy a unique name.
Write the policy using SQL.


------------------------------------------------

Storage Settings
Configure your project's storage settings
Upload file size limit

50

MB

MB
Equivalent to 52,428,800 bytes. Maximum size in bytes of a file that can be uploaded is 50 GB (53,687,091,200 bytes).

Enable Image Transformation


Optimize and resize images on the fly. Learn more.

Free Plan has a fixed upload file size limit of 50 MB.

Upgrade to the Pro Plan for a configurable upload file size limit of up to 50 GB.

Upgrade to Pro

Cancel

Save
S3 Connection
Connect to your bucket using any S3-compatible service via the S3 protocol
Docs
Enable connection via S3 protocol

Allow clients to connect to Supabase Storage via the S3 protocol
Endpoint
https://qlfmomqqbmusdvxycwhw.supabase.co/storage/v1/s3

Copy
Region
eu-west-3

Copy

Cancel

Save
S3 Access Keys
Manage your access keys for this project.

New access key
Description	Access key ID	Created at	
testKey	
e11f7229ad642e4750a0270114d23c5c

Copy
Today	



------------------------------------------------


Edit bucket "test"
Name of bucket
Buckets cannot be renamed once created.
test

Public bucket (True)
Anyone can read any object without any authorization
Additional configuration


Restrict file upload size for bucket
Prevent uploading of file sizes greater than a specified limit
Allowed MIME types
Comma separated values
e.g image/jpeg, image/png, audio/mpeg, video/mp4, etc
Wildcards are allowed, e.g. image/*. Leave blank to allow any MIME type.


------------------------------------------------

S3 Access Keys
Manage your access keys for this project.
i created this in the storage settings (supabase )
testKey:
Access key ID:
e11f7229ad642e4750a0270114d23c5c
Secret access key:
7091f5079ad777aa2c71a998ee593a565219f7abf4f148779f4c5f1ecfce5836


    # Upload to Supabase Storage
    s3 = boto3.client(
        's3',
        endpoint_url='https://qlfmomqqbmusdvxycwhw.supabase.co/storage/v1/s3',
        aws_access_key_id='e11f7229ad642e4750a0270114d23c5c',
        aws_secret_access_key='7091f5079ad777aa2c71a998ee593a565219f7abf4f148779f4c5f1ecfce5836',
        region_name='eu-west-3'

'test',  # Bucket name


