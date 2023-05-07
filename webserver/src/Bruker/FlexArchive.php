<?php
namespace App\Bruker;

use Iterator;
use RecursiveArrayIterator;
use RecursiveIteratorIterator;
use RuntimeException;
use ZipArchive;

/**
 * Represents a ZIP archive containing one or several {@see FlexSample}
 * acquired with Bruker Daltonics machines using the flexControl software.
 */
class FlexArchive {
    private ZipArchive $zip;

    /**
     * Class constructor
     *
     * @param string $path Path to archive
     * @throws RuntimeException if failed to read the archive
     */
    public function __construct(string $path) {
        $this->zip = new ZipArchive();
        $errorCode = $this->zip->open($path, ZipArchive::RDONLY);
        if ($errorCode !== true) {
            throw new RuntimeException("Failed to open the ZIP archive with error code $errorCode");
        }
    }

    /**
     * Class destructor
     */
    public function __destruct() {
        $this->zip->close();
    }

    /**
     * Get samples contained in the archive
     *
     * @return iterable<FlexSample> Samples
     */
    public function getSamples(): Iterator {
        $tree = [];
        $entrypoints = [];
        for ($index=0; $index<$this->zip->numFiles; $index++) {
            $path = $this->zip->getNameIndex($index);

            // Skip directories
            if (str_ends_with($path, '/')) {
                continue;
            }

            // Build file tree
            $parentNode =& $tree;
            $node =& $tree;
            $parts = explode('/', $path);
            foreach ($parts as $part) {
                $parentNode =& $node;
                $node =& $node[$part];
            }
            $node = $index;

            // Find entrypoint for samples by targeting "acqu" files
            if (str_ends_with($path, '/acqu')) {
                $basePath = mb_substr($path, 0, -5);
                $entrypoints[$basePath] =& $parentNode;
            }
        }

        // Parse each sample
        foreach ($entrypoints as $basePath=>&$node) {
            $sample = new FlexSample($basePath);

            // Add files to sample
            $iterator = new RecursiveIteratorIterator(new RecursiveArrayIterator($node));
            foreach ($iterator as $value) {
                $parts = [];
                for ($i=0; $i<=$iterator->getDepth(); $i++) {
                    $parts[] = $iterator->getSubIterator($i)->key();
                }
                $newPath = implode('/', $parts);
                $sample->addFile($newPath, $this->zip->getStreamIndex($value));
            }

            yield $sample;
        }
    }
}
