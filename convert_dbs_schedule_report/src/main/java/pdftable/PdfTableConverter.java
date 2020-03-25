package pdftable;
import net.digitaltsunami.tableextract.PdfProcessorException;
import net.digitaltsunami.tableextract.PdfTableExtractor;

import java.io.File;
import java.io.InputStream;

public class PdfTableConverter {
    public String extractTable(File inputFile) throws PdfProcessorException {
        PdfTableExtractor extractor = new PdfTableExtractor();
        return extractor.extractFile(inputFile);
    }
    public String extractTable(InputStream inputStream) throws PdfProcessorException {
        PdfTableExtractor extractor = new PdfTableExtractor();
        return extractor.extractTableFromStream(inputStream);
    }
}
