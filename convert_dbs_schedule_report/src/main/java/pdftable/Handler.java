package pdftable;

import com.amazonaws.AmazonServiceException;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.S3Event;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.event.S3EventNotification.S3EventNotificationRecord;
import com.amazonaws.services.s3.model.GetObjectRequest;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.util.StringInputStream;
import net.digitaltsunami.tableextract.PdfProcessorException;

import java.io.InputStream;

public class Handler implements
        RequestHandler<S3Event, String> {
    public String handleRequest(S3Event s3event, Context context) {
        try {
            S3EventNotificationRecord record = s3event.getRecords().get(0);

            String srcBucket = record.getS3().getBucket().getName();

            // Object key may have spaces or unicode non-ASCII characters.
            String srcKey = record.getS3().getObject().getUrlDecodedKey();

            String dstBucket = System.getenv("OUTPUT_DATA_BUCKET");
            if (dstBucket == null) {
                throw new IllegalArgumentException(
                        "No destination bucket.  Set OUTPUT_DATA_BUCKET env variable to output destination.");
            }
            String dstKey = srcKey.replaceAll(" ", "") + ".csv";

            // Sanity check: validate that source and destination are different
            // buckets.
            if (srcBucket.equals(dstBucket)) {
                System.out.println("Destination bucket must not match source bucket.");
                return "";
            }

            // Download the image from S3 into a stream
            AmazonS3 s3Client = AmazonS3ClientBuilder.defaultClient();
            S3Object s3Object = s3Client.getObject(new GetObjectRequest(
                    srcBucket, srcKey));
            InputStream objectData = s3Object.getObjectContent();

            // Extract shift schedule from report
            PdfTableConverter converter = new PdfTableConverter();
            String tableCsv = converter.extractTable(objectData);
            InputStream is = new StringInputStream(tableCsv);
            // Set Content-Length and Content-Type
            ObjectMetadata meta = new ObjectMetadata();
            meta.setContentLength(tableCsv.length());

            // Uploading to S3 destination bucket
            System.out.println("Writing to: " + dstBucket + "/" + dstKey);
            try {
                s3Client.putObject(dstBucket, dstKey, is, meta);
            } catch (AmazonServiceException e) {
                System.err.println(e.getErrorMessage());
                System.exit(1);
            }
            return "Ok";
        } catch (Exception | PdfProcessorException e) {
            throw new RuntimeException(e);
        }
    }
}
