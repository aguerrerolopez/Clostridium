<?php
namespace App\Bruker;

use DateTime;
use RuntimeException;
use ZipArchive;

/**
 * A single sample extracted from a {@see FlexArchive} instance.
 */
class FlexSample {
    const MAX_FILES = 20;
    const MAX_FILESIZE = 200_000; // In bytes, typically "fid" is the largest with about 85,000 bytes
    const MIN_DATETIME = '2010-01-01 00:00:00 UTC'; // Minimum allowed value in timestamps
    const MAX_DATETIME = '+1 day'; // Maximum allowed value in timestamps

    private string $basePath;

    /** @var array<string,string|resource> */
    private array $files = [];

    /** @var array<string,array<string,string>> */
    private array $metadata = [];

    /**
     * Class constructor
     *
     * @param string $basePath Path to sample directory (relative to archive were it was obtained from)
     */
    public function __construct(string $basePath) {
        $this->basePath = $basePath;
    }

    /**
     * Get base path
     *
     * @return string Base path
     */
    public function getBasePath(): string {
        return $this->basePath;
    }

    /**
     * Add file to sample
     *
     * @param  string          $path Relative path to file
     * @param  string|resource $data File contents or handle to stream
     * @return static                This instance
     */
    public function addFile(string $path, $data): static {
        $this->files[$path] = $data;
        return $this;
    }

    /**
     * Get file contents
     *
     * @param  string $path Relative path to file
     * @return string       File contents
     * @throws RuntimeException if invalid path or failed to get contents
     */
    private function getFileContents(string $path): string {
        $data =& $this->files[$path];

        // Validate path
        if (!isset($data)) {
            throw new RuntimeException("Cannot find file \"$path\"");
        }

        // Copy contents from stream (if needed)
        if (is_resource($data)) {
            $data = stream_get_contents($data, self::MAX_FILESIZE+1, 0); // Note the additional byte
            if ($data === false) {
                throw new RuntimeException("Failed to read file \"$path\"");
            }
            if (strlen($data) > self::MAX_FILESIZE) {
                throw new RuntimeException("File \"$path\" is too large");
            }
        }

        // Return value
        return $data;
    }

    /**
     * Get metadata value
     *
     * @param  string $path  Relative path to metadata fle
     * @param  string $field Field name
     * @return string        Field value or `null` if not found
     * @throws RuntimeException if not a valid metadata file or field not found
     */
    private function getMetadata(string $path, string $field): string {
        $metadata =& $this->metadata[$path];

        // Parse metadata file (if needed)
        if (!isset($metadata)) {
            $data = $this->getFileContents($path);
            $data = str_replace("\r\n", "\n", $data);
            $data = explode('##', $data);

            // Read each field
            $metadata = [];
            foreach ($data as $row) {
                if (!str_contains($row, '=')) {
                    continue;
                }
                list($key, $value) = explode('=', $row, 2);
                $value = trim($value);
                if (mb_substr($value, 0, 1) === '<' && mb_substr($value, -1) === '>') {
                    $value = mb_substr($value, 1, -1);
                }
                $metadata[$key] = $value;
            }
        }

        // Return metadata value
        if (!isset($metadata[$field])) {
            throw new RuntimeException("Missing field $field from \"$path\"");
        }
        return $metadata[$field];
    }

    /**
     * Get sample ID
     *
     * @return string Sample ID as hexadecimal string
     * @throws RuntimeException if failed to extract metadata
     */
    public function getSampleId(): string {
        $sampleId = $this->getMetadata('acqu', '$ID_raw');
        $sampleId = str_replace('-', '', $sampleId);
        if (!preg_match('/^[a-f0-9]{32}$/', $sampleId)) {
            throw new RuntimeException('Invalid sample ID ($ID_raw)');
        }
        return $sampleId;
    }

    /**
     * Get target ID
     *
     * @return string Target ID as hexadecimal string
     * @throws RuntimeException if failed to extract metadata
     */
    public function getTargetId(): string {
        $targetId = $this->getMetadata('acqu', '$TgIDS');
        $targetId = str_replace('_', '', $targetId);
        if (!preg_match('/^G[A-F0-9]{32}$/', $targetId)) {
            throw new RuntimeException('Invalid target ID ($TgIDS)');
        }
        $targetId = substr($targetId, 1); // Remove first "G" character
        $targetId = strtolower($targetId);
        return $targetId;
    }

    /**
     * Get acquisition date
     *
     * @return DateTime Acquisition date
     * @throws RuntimeException if failed to extract metadata
     */
    public function getAcquisitionDate(): DateTime {
        $acquisitionDate = $this->getMetadata('acqu', '$AQ_DATE');
        $acquisitionDate = DateTime::createFromFormat(DateTime::RFC3339_EXTENDED, $acquisitionDate);
        if ($acquisitionDate === false) {
            throw new RuntimeException('Invalid acquisition date format ($AQ_DATE)');
        }
        if ($acquisitionDate->getTimestamp() < strtotime(self::MIN_DATETIME)) {
            throw new RuntimeException('Acquisition date is too old ($AQ_DATE)');
        }
        if ($acquisitionDate->getTimestamp() > strtotime(self::MAX_DATETIME)) {
            throw new RuntimeException('Acquisition date is in the future ($AQ_DATE)');
        }
        return $acquisitionDate;
    }

    /**
     * Get instrument serial number
     *
     * @return string Instrument serial number
     * @throws RuntimeException if failed to extract metadata
     */
    public function getInstrumentSerialNumber(): string {
        $serialNumber = $this->getMetadata('acqu', '$InstrID');
        if (!preg_match('/^[0-9]{1,12}\.[0-9]{5}$/', $serialNumber)) {
            throw new RuntimeException('Invalid instrument serial number ($InstrID)');
        }
        return $serialNumber;
    }

    /**
     * Get instrument type
     *
     * @return int Instrument type
     * @throws RuntimeException if failed to extract metadata
     */
    public function getInstrumentType(): int {
        $type = $this->getMetadata('acqu', '$InstTyp');
        if (!preg_match('/^([0-9]|10)$/', $type)) { // From 0 to 10
            throw new RuntimeException('Invalid instrument type ($InstTyp)');
        }
        return (int) $type;
    }

    /**
     * Get digitizer type
     *
     * @return int Digitizer type
     * @throws RuntimeException if failed to extract metadata
     */
    public function getDigitizerType(): int {
        $type = $this->getMetadata('acqu', '$DIGTYP');
        if (!preg_match('/^1?[0-9]$/', $type)) { // From 0 to 19
            throw new RuntimeException('Invalid digitizer type ($DIGTYP)');
        }
        return (int) $type;
    }

    /**
     * Get sample position
     *
     * @return string Sample position (aka "pocillo")
     * @throws RuntimeException if failed to extract metadata
     */
    public function getPosition(): string {
        $position = $this->getMetadata('acqu', '$PATCHNO');
        if (!preg_match('/^[A-Z][0-9]{1,2}$/', $position)) {
            throw new RuntimeException('Invalid sample position ($PATCHNO)');
        }
        return $position;
    }

    /**
     * Get path where sample was originally saved to
     *
     * @return string Original path
     * @throws RuntimeException if failed to extract metadata
     */
    public function getOriginalPath(): string {
        $path = $this->getMetadata('acqu', '$PATH');
        $path = trim($path);
        if (empty($path)) {
            throw new RuntimeException('Invalid sample path ($PATH)');
        }
        $path = str_replace('\\', '/', $path);
        return $path;
    }

    /**
     * Get flexControl version
     *
     * @return string flexControl version
     * @throws RuntimeException if failed to extract metadata
     */
    public function getFlexControlVersion(): string {
        $version = $this->getMetadata('acqu', '$FCVer');
        if (!preg_match('/^flexControl [0-9.]+[0-9]+$/', $version)) {
            throw new RuntimeException('Invalid flexControl version ($FCVer)');
        }
        $version = substr($version, 12); // Remove "flexControl " from response
        return $version;
    }

    /**
     * Get AIDA version
     *
     * @return string AIDA version
     * @throws RuntimeException if failed to extract metadata
     */
    public function getAidaVersion(): string {
        $version = $this->getMetadata('pdata/1/proc', '$Acquver');
        if (!preg_match('/^AIDA[0-9.]+[0-9]+$/', $version)) {
            throw new RuntimeException('Invalid AIDA version ($Acquver)');
        }
        $version = substr($version, 4); // Remove "AIDA" from response
        return $version;
    }

    /**
     * Get calibration date
     *
     * @return DateTime Calibration date
     * @throws RuntimeException if failed to extract metadata
     */
    public function getCalibrationDate(): DateTime {
        $calibrationDate = $this->getMetadata('pdata/1/proc', '$CLDATE');
        $calibrationDate = DateTime::createFromFormat(DateTime::RFC3339_EXTENDED, $calibrationDate);
        if ($calibrationDate === false) {
            throw new RuntimeException('Invalid calibration date format ($CLDATE)');
        }
        if ($calibrationDate->getTimestamp() < strtotime(self::MIN_DATETIME)) {
            throw new RuntimeException('Calibration date is too old ($CLDATE)');
        }
        if ($calibrationDate->getTimestamp() > strtotime(self::MAX_DATETIME)) {
            throw new RuntimeException('Calibration date is in the future ($CLDATE)');
        }
        return $calibrationDate;
    }

    /**
     * Get digest of sample contents
     *
     * @return string SHA-256 digest as hexadecimal string
     */
    public function getDigest(): string {
        // Sort paths of files in sample (to be deterministic)
        $sortedPaths = array_keys($this->files);
        sort($sortedPaths);

        // Compute hash of contents
        $ctx = hash_init('sha256');
        foreach ($sortedPaths as $path) {
            hash_update($ctx, $this->getFileContents($path));
        }
        return hash_final($ctx);
    }

    /**
     * Validate sample
     *
     * @throws RuntimeException if failed to pass validation
     */
    public function validate(): void {
        // Limit the number of files per sample
        if (count($this->files) > self::MAX_FILES) {
            throw new RuntimeException('Too many files in sample');
        }

        // Preload each file entry
        foreach (array_keys($this->files) as $path) {
            $this->getFileContents($path);
        }

        // Validate spectrum type
        if (trim($this->getFileContents('sptype')) !== 'tof') {
            throw new RuntimeException('Spectrum type must be time-of-flight (ToF)');
        }

        // Validate spectrum
        $spectrumBytes = strlen($this->getFileContents('fid'));
        if (($spectrumBytes % 4) !== 0) {
            throw new RuntimeException('Spectrum file ("fid") has an invalid size');
        }

        // Validate acquisition metadata
        if (mb_strtolower($this->getMetadata('acqu', 'TITLE')) !== 'xmass parameter file') {
            throw new RuntimeException('Acquisition metadata is not an XMASS Parameter file');
        }
        $this->getSampleId();
        $this->getTargetId();
        $this->getAcquisitionDate();
        $this->getInstrumentSerialNumber();
        $this->getInstrumentType();
        $this->getDigitizerType();
        $this->getPosition();
        $this->getOriginalPath();
        $this->getFlexControlVersion();

        // Validate calibration metadata
        if (mb_strtolower($this->getMetadata('pdata/1/proc', 'TITLE')) !== 'xmass parameter file') {
            throw new RuntimeException('Calibration metadata is not an XMASS Parameter file');
        }
        $this->getAidaVersion();
        $this->getCalibrationDate();
    }

    /**
     * Export sample as ZIP archive
     *
     * @param string $path Destination path
     * @throws RuntimeException if failed to export sample
     */
    public function export(string $path): void {
        $zip = new ZipArchive();
        $errorCode = $zip->open($path, ZipArchive::CREATE | ZipArchive::OVERWRITE);
        if ($errorCode !== true) {
            throw new RuntimeException("Failed to open $path for writing with error code $errorCode");
        }

        // Add files
        $acquiredAtTimestamp = $this->getAcquisitionDate()->getTimestamp();
        foreach (array_keys($this->files) as $path) {
            $zip->addFromString($path, $this->getFileContents($path));
            $zip->setMtimeName($path, $acquiredAtTimestamp);
        }

        // Write to disk
        $zip->close();
    }
}
