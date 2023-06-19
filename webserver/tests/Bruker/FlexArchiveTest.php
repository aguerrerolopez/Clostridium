<?php
namespace Tests\Bruker;

use App\Bruker\FlexArchive;
use App\Bruker\FlexSample;
use DateTime;
use PHPUnit\Framework\TestCase;
use RuntimeException;
use ZipArchive;

final class FlexArchiveTest extends TestCase {
    public function testParsesFlexArchives(): void {
        $archive = new FlexArchive(__DIR__ . '/samples-valid.zip');
        /** @var array<string,FlexSample> */
        $samples = [];

        // Validate all samples
        foreach ($archive->getSamples() as $sample) {
            $sample->validate();
            $samples[$sample->getBasePath()] = $sample;
        }
        $this->assertEquals(6, count($samples), 'Invalid number of samples');

        // Sample #1
        $sample = $samples['23050678/0_E1/1/1SLin'];
        $this->assertEquals('16824b6eacf14b9d861cd7d18b6a1237',           $sample->getSampleId());
        $this->assertEquals('fe4feffa0c054941b01db2dedef2f95f',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2023-02-22T12:47:40.909+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E1',                                         $sample->getPosition());
        $this->assertEquals('3.4.207.20',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2023-02-21T08:58:28.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('spectra/230222-1244-1011026579/23050678/0_E1/1/1SLin', $sample->getOriginalPath());
        $this->assertEquals('bfe8ac98a91030ce8a7d5e50cd790af4a56411a76414ace22994f784efc82e05', $sample->getDigest());

        // Sample #2
        $sample = $samples['23050678/0_E2/1/1SLin'];
        $this->assertEquals('d7dca0effaf247d2abb86188f4e635ed',           $sample->getSampleId());
        $this->assertEquals('fe4feffa0c054941b01db2dedef2f95f',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2023-02-22T12:47:45.482+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E2',                                         $sample->getPosition());
        $this->assertEquals('3.4.207.20',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2023-02-21T08:58:28.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('spectra/230222-1244-1011026579/23050678/0_E2/1/1SLin', $sample->getOriginalPath());
        $this->assertEquals('438066211432312e9e5a7624d6f7c844d898ede2432811e8d540a39764d8769e', $sample->getDigest());

        // Sample #3
        $sample = $samples['23050679/0_E3/1/1SLin'];
        $this->assertEquals('04d447db393d422981e8c10c90ec09b2',           $sample->getSampleId());
        $this->assertEquals('fe4feffa0c054941b01db2dedef2f95f',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2023-02-22T12:47:50.935+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E3',                                         $sample->getPosition());
        $this->assertEquals('3.4.207.20',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2023-02-21T08:58:28.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('spectra/230222-1244-1011026579/23050679/0_E3/1/1SLin', $sample->getOriginalPath());
        $this->assertEquals('b5ee174616023632b6065ac5cefc44913dfcf9e055bf6d7a6c17b48a211cbd29', $sample->getDigest());

        // Sample #4
        $sample = $samples['23050679/0_E4/1/1SLin'];
        $this->assertEquals('fb60fc50f99942bba40e0bcc5e262e1d',           $sample->getSampleId());
        $this->assertEquals('fe4feffa0c054941b01db2dedef2f95f',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2023-02-22T12:48:05.828+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E4',                                         $sample->getPosition());
        $this->assertEquals('3.4.207.20',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2023-02-21T08:58:28.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('spectra/230222-1244-1011026579/23050679/0_E4/1/1SLin', $sample->getOriginalPath());
        $this->assertEquals('3e04f72432353ac262d1ae2035518bfe533886d2e8e93ec3fe05c0c212624cba', $sample->getDigest());

        // Sample #5
        $sample = $samples['Clostridium difficile 239295-027/D3/0_E1/1/1SLin'];
        $this->assertEquals('ce9421f2726c4c5aa68dd08a4b61477d',           $sample->getSampleId());
        $this->assertEquals('649ec898d5e94625973438813e13596c',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2020-03-15T18:34:25.353+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E1',                                         $sample->getPosition());
        $this->assertEquals('3.4.204.10',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2020-03-13T16:21:05.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('D:/INVESTIGACION MALDI/Clostridium difficile/24 INICIALES/D3/Clostridium difficile 239295-027/0_E1/1/1SLin', $sample->getOriginalPath());
        $this->assertEquals('99677068538895f492c20a0583dae41d9832a0d2bdbe796febab623aebb69854', $sample->getDigest());

        // Sample #6
        $sample = $samples['Clostridium difficile 239295-027/D3/0_E1/2/1SLin'];
        $this->assertEquals('ddd4be612b6d42b9ada6e4df0634db79',           $sample->getSampleId());
        $this->assertEquals('649ec898d5e94625973438813e13596c',           $sample->getTargetId());
        $this->assertEquals(new DateTime('2020-03-15T18:34:41.306+0100'), $sample->getAcquisitionDate());
        $this->assertEquals('8604832.05252',                              $sample->getInstrumentSerialNumber());
        $this->assertEquals(9,                                            $sample->getInstrumentType());
        $this->assertEquals(19,                                           $sample->getDigitizerType());
        $this->assertEquals('E1',                                         $sample->getPosition());
        $this->assertEquals('3.4.204.10',                                 $sample->getFlexControlVersion());
        $this->assertEquals('4.7.373.7',                                  $sample->getAidaVersion());
        $this->assertEquals(new DateTime('2020-03-13T16:21:05.000+0000'), $sample->getCalibrationDate());
        $this->assertEquals('D:/INVESTIGACION MALDI/Clostridium difficile/24 INICIALES/D3/Clostridium difficile 239295-027/0_E1/2/1SLin', $sample->getOriginalPath());
        $this->assertEquals('3a13229aafd4534198f1d9d181c73b7371ab252166a03c4c2330f972ad30755d', $sample->getDigest());
    }

    public function testParsesFlexArchivesWithSingleSample(): void {
        $archive = new FlexArchive(__DIR__ . '/samples-valid-single.zip');
        /** @var FlexSample[] */
        $samples = [...$archive->getSamples()];
        $this->assertEquals(1, count($samples), 'Invalid count of samples');
        $this->assertEquals('', $samples[0]->getBasePath());
        $samples[0]->validate();
    }

    public function testThrowsExceptionForInvalidArchives(): void {
        $this->expectException(RuntimeException::class);
        new FlexArchive(__DIR__ . '/samples-invalid.rar');
    }

    public function testExportsSampleToZipArchive(): void {
        $archive = new FlexArchive(__DIR__ . '/samples-valid.zip');
        foreach ($archive->getSamples() as $sample) {
            // Export sample
            $tmpPath = tempnam(sys_get_temp_dir(), 'flx');
            $sample->export($tmpPath);

            // Make sure it's a valid ZIP archive
            $zip = new ZipArchive();
            $this->assertSame(true, $zip->open($tmpPath, ZipArchive::RDONLY), 'Exported sample is not a valid ZIP archive');
            $this->assertNotSame(false, $zip->locateName('acqu'), 'Missing "acqu" file from exported sample');
            $zip->close();

            // Clean-up
            unlink($tmpPath);
        }
    }
}
