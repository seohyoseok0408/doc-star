package com.docstar;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class DocStarApplication {

	public static void main(String[] args) {
		SpringApplication.run(DocStarApplication.class, args);
	}

}
