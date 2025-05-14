from lambda_function import scrape_dummy, generate_report_no_pandas

if __name__ == "__main__":
    keyword = "ceramic mug"
    job_id = "test-job-123"
    scraped_data = scrape_dummy(keyword, job_id)
    print("Scraped Data:", scraped_data)

    report_path = generate_report_no_pandas(scraped_data, job_id)
    print(f"Report generated at: {report_path}")

    with open(report_path, 'r', encoding='utf-8') as f:
        print("CSV Contents:")
        print(f.read())