<?php
namespace Tests\Bruker;

use App\Bruker\FlexArchive;
use App\Bruker\FlexSample;
use DateTime;
use PHPUnit\Framework\TestCase;
use RuntimeException;

final class FlexArchiveTest extends TestCase {
    public function testParsesRawFlexArchives(): void {
        $archive = new FlexArchive(__DIR__ . '/samples-valid.zip');
        /** @var array<string,FlexSample[]> */
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
    }

    public function testThrowsExceptionForInvalidArchives(): void {
        $this->expectException(RuntimeException::class);
        new FlexArchive(__DIR__ . '/samples-invalid.rar');
    }
}